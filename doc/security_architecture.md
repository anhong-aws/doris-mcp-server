# Doris MCP Server 安全架构详解

## 1. 概述

Doris MCP Server 采用多层次安全架构，涵盖身份认证、权限控制、数据脱敏、SQL安全校验等核心安全能力。本文档从配置到使用层面全面讲解其安全机制。

## 2. 配置层安全体系

### 2.1 Token 配置文件结构

在 `tokens.json` 中定义了基于 Token 的认证配置，每个 Token 包含完整的安全元数据和数据库连接配置：

```json
{
  "version": "1.0",
  "tokens": [
    {
      "token_id": "admin-token",
      "token": "doris_admin_token_123456",
      "description": "Doris admin API access token",
      "expires_hours": null,
      "is_active": true,
      "database_config": {
        "host": "127.0.0.1",
        "port": 9030,
        "user": "root",
        "password": "",
        "database": "information_schema",
        "charset": "UTF8",
        "fe_http_port": 8030
      }
    }
  ]
}
```

这种设计实现了**Token 绑定的数据库配置**特性，每个 Token 可以配置独立的数据库连接参数，从而实现：

- 不同 Token 访问不同数据库实例
- 基于 Token 的数据源隔离
- 精细化的数据库连接权限控制

### 2.2 环境配置与安全开关

在 `.env` 和 `DorisConfig` 类中定义了全局安全开关：

```python
# 安全认证开关配置
enable_token_auth = True           # 启用 Token 认证
enable_jwt_auth = True             # 启用 JWT 认证
enable_oauth_auth = False          # 启用 OAuth 认证

# HTTP 模式下的 Token 管理安全配置
enable_http_token_management = False
allowed_token_management_ips = ["127.0.0.1"]
```

这些配置决定了系统采用何种认证方式以及敏感端点的访问控制策略。

## 3. 身份认证机制

### 3.1 多认证 Provider 架构

`DorisSecurityManager` 内部维护了多个认证 Provider，支持**任意一种认证方式成功即可访问**的灵活策略：

```python
class AuthenticationProvider:
    def __init__(self, config, security_manager=None):
        self.config = config
        self.logger = get_logger(__name__)
        self.session_cache = {}
        self.jwt_manager = None
        self.oauth_provider = None
        self.token_manager = None
        
        # 根据配置开关初始化不同的认证方式
        if config.security.enable_token_auth:
            self._initialize_token_manager()
            
        if config.security.enable_jwt_auth:
            self._initialize_jwt_manager()
            
        if config.security.enable_oauth_auth:
            self._initialize_oauth_provider()
```

认证优先级顺序为：Token → JWT → OAuth。

### 3.2 认证上下文管理

认证成功后创建 `AuthContext` 对象，包含完整的身份信息和权限上下文：

```python
@dataclass
class AuthContext:
    """认证上下文，用于审计和会话跟踪"""
    
    token_id: str = ""                          # Token标识，用于审计
    user_id: str = ""                           # 用户标识
    roles: list[str] = field(default_factory=list)   # 用户角色列表
    permissions: list[str] = field(default_factory=list)  # 权限列表
    security_level: SecurityLevel = field(default_factory=lambda: SecurityLevel.INTERNAL)  # 安全级别
    client_ip: str = "unknown"                  # 客户端IP
    session_id: str = ""                        # 会话ID
    login_time: datetime = field(default_factory=datetime.utcnow)  # 登录时间
    last_activity: datetime | None = None       # 最后活动时间
    token: str = ""                             # 原始Token（用于绑定数据库配置）
```

这个上下文对象贯穿整个请求生命周期，用于后续的权限校验和数据脱敏处理。

### 3.3 认证请求处理

```python
async def authenticate_request(self, auth_info: dict[str, Any]) -> AuthContext:
    """验证请求认证信息
    
    按顺序尝试认证方法：Token -> JWT -> OAuth
    任意一种方法成功即可访问
    如果所有方法都禁用，则返回匿名上下文
    """
    # 检查是否启用了任何认证方法
    if not (self.config.security.enable_token_auth or 
            self.config.security.enable_jwt_auth or 
            self.config.security.enable_oauth_auth):
        self.logger.debug("All authentication methods are disabled")
        # 当没有启用认证时返回匿名上下文
        return AuthContext(
            token_id="anonymous",
            user_id="anonymous",
            roles=["anonymous"],
            permissions=["read"],
            security_level=SecurityLevel.PUBLIC,
            client_ip=auth_info.get("client_ip", "unknown"),
            session_id="anonymous_session"
        )
    
    # 按优先级顺序尝试认证方法
    last_error = None
    
    # 1. 首先尝试 Token 认证（最常用）
    if self.config.security.enable_token_auth:
        try:
            return await self.auth_provider.authenticate_token(auth_info)
        except Exception as e:
            self.logger.debug(f"Token authentication failed: {e}")
            last_error = e
    
    # 2. 尝试 JWT 认证
    if self.config.security.enable_jwt_auth:
        try:
            return await self.auth_provider.authenticate_jwt(auth_info)
        except Exception as e:
            self.logger.debug(f"JWT authentication failed: {e}")
            last_error = e
    
    # 3. 尝试 OAuth 认证
    if self.config.security.enable_oauth_auth:
        try:
            return await self.auth_provider.authenticate_oauth(auth_info)
        except Exception as e:
            self.logger.debug(f"OAuth authentication failed: {e}")
            last_error = e
    
    # 所有启用的认证方法都失败
    error_message = f"Authentication failed: {str(last_error)}" if last_error else "No authentication method succeeded"
    self.logger.warning(f"Authentication failed for client {auth_info.get('client_ip', 'unknown')}: {error_message}")
    raise ValueError(error_message)
```

### 3.4 匿名访问机制

当所有认证方式都关闭时，系统返回**匿名上下文**，允许有限访问：

```python
# 当认证禁用时返回的匿名上下文
AuthContext(
    token_id="anonymous",
    user_id="anonymous",
    roles=["anonymous"],
    permissions=["read"],
    security_level=SecurityLevel.PUBLIC,
    client_ip=auth_info.get("client_ip", "unknown"),
    session_id="anonymous_session"
)
```

## 4. 权限控制体系

### 4.1 基于角色的访问控制

`AuthorizationProvider` 实现了细粒度的权限控制，支持角色和资源级别的权限校验：

```python
async def authorize_resource_access(
    self, auth_context: AuthContext, resource_uri: str
) -> bool:
    """验证资源访问权限"""
    return await self.authz_provider.check_permission(
        auth_context, resource_uri, "read"
    )
```

### 4.2 权限模型

权限模型包含以下核心概念：

| 权限要素 | 说明 |
|---------|------|
| **角色权限** | 基于用户角色分配权限，支持角色继承和组合 |
| **资源权限** | 基于资源URI进行访问控制，支持通配符匹配 |
| **操作权限** | 区分read、write、execute等操作类型 |
| **安全级别** | 基于数据敏感度的访问控制（PUBLIC/INTERNAL/CONFIDENTIAL/SECRET） |

### 4.3 Token 管理 API 安全

HTTP 模式的 Token 管理端点受到**多层安全保护**：

```python
class TokenSecurityMiddleware:
    """Token 管理安全中间件"""
    
    def __init__(self, config):
        self.allowed_ips = config.get("allowed_token_management_ips", ["127.0.0.1"])
        self.admin_token_id = config.get("admin_token_id", "admin-token")
    
    async def check_token_management_access(self, request: Request):
        """检查 Token 管理访问权限"""
        
        # 1. IP地址检查：仅允许 localhost 访问
        client_ip = request.client.host
        if client_ip not in self.allowed_ips:
            return JSONResponse({
                "error": "Access denied",
                "message": "Token management is restricted to localhost only",
                "client_ip": client_ip,
                "allowed_ips": self.allowed_ips
            }, status_code=403)
        
        # 2. 管理员 Token 校验
        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            admin_token = authorization[7:]
        else:
            admin_token = authorization
        
        if not self._validate_admin_token(admin_token):
            return JSONResponse({
                "error": "Invalid admin token",
                "message": "Token management requires valid admin credentials"
            }, status_code=401)
        
        # 3. 检查 Token 管理是否已启用
        if not self._is_management_enabled():
            return JSONResponse({
                "error": "Token management is disabled",
                "message": "HTTP token management must be explicitly enabled in configuration"
            }, status_code=403)
        
        return None  # 通过所有检查，允许访问
```

### 4.4 Token 管理端点保护示例

```python
class TokenHandlers:
    """Token 认证 HTTP 处理器"""
    
    def __init__(self, security_manager, config=None):
        self.security_manager = security_manager
        self.logger = get_logger(__name__)
        
        # 初始化安全中间件
        if config:
            self.security_middleware = TokenSecurityMiddleware(config)
        else:
            self.security_middleware = None
            self.logger.warning("Token handlers initialized without security middleware - access control disabled")
    
    async def handle_create_token(self, request: Request) -> JSONResponse:
        """处理 Token 创建请求"""
        # 应用安全检查
        if self.security_middleware:
            security_response = await self.security_middleware.check_token_management_access(request)
            if security_response:
                return security_response
        
        # ... Token 创建逻辑
```

## 5. MCP Tools 权限集成

### 5.1 Tool 定义与权限标注

在 `bi_tools_manager.py` 中定义的所有 Tool 都经过权限校验流程：

```python
async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
    """
    Tool 路由和调度中心
    """
    try:
        start_time = time.time()
        
        # 1. 从请求中提取认证信息
        auth_info = await self._extract_auth_info(request)
        
        # 2. 执行身份认证
        auth_context = await self.security_manager.authenticate_request(auth_info)
        
        # 3. 执行 SQL 安全校验（仅 exec_query 需要）
        if name == "exec_query":
            sql_validation = await self.security_manager.validate_sql_security(
                arguments.get("sql"), auth_context
            )
            if not sql_validation.is_valid:
                raise ValueError(sql_validation.error_message)
        
        # 4. 执行 Tool 调用
        if name == "exec_query":
            result = await self._exec_query_tool(arguments)
        elif name == "get_table_schema":
            result = await self._get_table_schema_tool(arguments)
        elif name == "get_db_table_list":
            result = await self._get_db_table_list_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        execution_time = time.time() - start_time
        
        # 5. 应用数据脱敏
        if isinstance(result, dict) and "data" in result:
            result["data"] = await self.security_manager.apply_data_masking(
                result["data"], auth_context
            )
        
        # 6. 添加执行信息
        if isinstance(result, dict):
            result["_execution_info"] = {
                "tool_name": name,
                "execution_time": round(execution_time, 3),
                "timestamp": datetime.now().isoformat(),
            }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Tool call failed {name}: {str(e)}")
        error_result = {
            "error": str(e),
            "tool_name": name,
            "arguments": arguments,
            "timestamp": datetime.now().isoformat(),
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)
```

### 5.2 Tool 级别安全控制

当前系统定义了三个核心 Tool，每个 Tool 有不同的安全要求：

| Tool 名称 | 功能描述 | 权限要求 | 安全考量 |
|---------|---------|---------|---------|
| `exec_query` | 执行 SQL 查询 | 需要数据库执行权限 | 最高风险，需 SQL 注入防护和敏感操作拦截 |
| `get_table_schema` | 获取表结构 | 需元数据读取权限 | 中等风险，涉及数据库结构信息泄露 |
| `get_db_table_list` | 获取表列表 | 需元数据读取权限 | 低风险，仅返回表名列表 |

### 5.3 Tool 定义示例

```python
async def list_tools(self) -> List[Tool]:
    """列出所有可用的查询工具（用于 stdio 模式）"""
    
    tools = [
        Tool(
            name="exec_query",
            description="""[功能描述]: 执行 SQL 查询并返回结果，支持目录联邦查询。

[参数说明]:

- sql (string) [必填] - 要执行的 SQL 语句。必须使用三段式命名引用所有表：'catalog_name.db_name.table_name'。内部表使用 'internal.db_name.table_name'，外部表使用 'catalog_name.db_name.table_name'

- db_name (string) [可选] - 目标数据库名称，默认为当前数据库

- catalog_name (string) [可选] - 引用目录名称，默认为当前目录

- max_rows (integer) [可选] - 返回的最大行数，默认 100

- timeout (integer) [可选] - 查询超时时间（秒），默认 30
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "要执行的 SQL 语句，必须使用三段式命名"},
                    "db_name": {"type": "string", "description": "目标数据库名称"},
                    "catalog_name": {"type": "string", "description": "目录名称"},
                    "max_rows": {"type": "integer", "description": "返回的最大行数", "default": 100},
                    "timeout": {"type": "integer", "description": "超时时间（秒）", "default": 30},
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="get_table_schema",
            description="""[功能描述]: 获取指定表的详细结构信息（列、类型、注释等）。

[参数说明]:

- table_name (string) [必填] - 要查询的表名

- db_name (string) [可选] - 目标数据库名称，默认为当前数据库
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "表名"},
                    "db_name": {"type": "string", "description": "数据库名"},
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="get_db_table_list",
            description="""[功能描述]: 获取指定数据库中的所有表名列表。

[参数说明]:

- db_name (string) [可选] - 目标数据库名称，默认为当前数据库
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "db_name": {"type": "string", "description": "数据库名称"},
                },
            },
        ),
    ]
    
    return tools
```

## 6. SQL 安全防护

### 6.1 危险操作拦截

系统内置 SQL 安全校验器，阻止危险操作：

```python
def _load_blocked_keywords(self) -> set[str]:
    """从配置加载被阻止的 SQL 关键字"""
    blocked_keywords = [
        "DROP",      # 删除操作
        "CREATE",    # 创建操作
        "ALTER",     # 修改操作
        "TRUNCATE",  # 清空表
        "DELETE",    # 删除数据
        "INSERT",    # 插入数据
        "UPDATE",    # 更新数据
        "GRANT",     # 授权操作
        "REVOKE",    # 回收权限
        "EXEC",      # 执行存储过程
        "EXECUTE",
        "SHUTDOWN",  # 关闭服务
        "KILL"       # 终止进程
    ]
    return set(blocked_keywords)
```

### 6.2 SQL 校验流程

```python
@dataclass
class ValidationResult:
    """校验结果"""
    is_valid: bool
    error_message: str | None = None
    risk_level: str = "low"
    blocked_operations: list[str] = None
    
    def __post_init__(self):
        if self.blocked_operations is None:
            self.blocked_operations = []

async def validate_sql_security(
    self, sql: str, auth_context: AuthContext
) -> ValidationResult:
    """验证 SQL 查询安全性"""
    
    # 1. 解析 SQL 语句
    parsed_statements = sqlparse.parse(sql)
    
    # 2. 检查危险关键词
    blocked_ops = []
    for statement in parsed_statements:
        if self._contains_blocked_keyword(statement):
            blocked_ops.extend(self._identify_blocked_operations(statement))
    
    if blocked_ops:
        return ValidationResult(
            is_valid=False,
            error_message="SQL contains blocked operations",
            risk_level="high",
            blocked_operations=blocked_ops
        )
    
    # 3. 检查表访问权限
    for statement in parsed_statements:
        for table in self._extract_tables(statement):
            if not self._check_table_access(auth_context, table):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"No permission to access table: {table}"
                )
    
    # 4. 检查查询类型权限
    query_type = self._identify_query_type(sql.upper())
    if query_type in ["WRITE", "DDL", "ADMIN"] and not self._has_write_permission(auth_context):
        return ValidationResult(
            is_valid=False,
            error_message=f"Permission denied for {query_type} operations"
        )
    
    return ValidationResult(is_valid=True)

def _contains_blocked_keyword(self, statement: Statement) -> bool:
    """检查语句是否包含被阻止的关键字"""
    statement_str = str(statement).upper()
    return any(keyword in statement_str for keyword in self.blocked_keywords)
```

### 6.3 SQL 安全校验器类

```python
class SQLSecurityValidator:
    """SQL 安全校验器"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        
        # 加载阻塞的关键字
        self.blocked_keywords = self._load_blocked_keywords()
        
        # 加载敏感表配置
        self.sensitive_tables = self._load_sensitive_tables()
    
    def _identify_query_type(self, sql: str) -> str:
        """识别 SQL 查询类型"""
        if any(keyword in sql for keyword in ["INSERT", "UPDATE", "DELETE"]):
            return "WRITE"
        elif any(keyword in sql for keyword in ["CREATE", "ALTER", "DROP", "TRUNCATE"]):
            return "DDL"
        elif any(keyword in sql for keyword in ["GRANT", "REVOKE", "SET", "SHOW"]):
            return "ADMIN"
        return "READ"
    
    async def validate(self, sql: str, auth_context: AuthContext) -> ValidationResult:
        """执行 SQL 安全校验"""
        try:
            # 基础校验
            result = await self._basic_security_check(sql, auth_context)
            
            if not result.is_valid:
                return result
            
            # 高级校验
            result = await self._advanced_security_check(sql, auth_context)
            
            return result
            
        except Exception as e:
            self.logger.error(f"SQL validation error: {e}")
            return ValidationResult(
                is_valid=False,
                error_message=f"Validation error: {str(e)}",
                risk_level="medium"
            )
```

## 7. 数据脱敏机制

### 7.1 敏感数据分类

系统定义了四级数据敏感度：

```python
class SecurityLevel(Enum):
    """安全级别枚举"""
    
    PUBLIC = "public"         # 公开数据，无需脱敏
    INTERNAL = "internal"     # 内部数据，默认脱敏
    CONFIDENTIAL = "confidential"  # 机密数据，强脱敏
    SECRET = "secret"         # 绝密数据，禁止访问
```

### 7.2 敏感表配置

```python
def _load_sensitive_tables(self) -> dict[str, SecurityLevel]:
    """加载敏感表配置"""
    default_tables = {
        "user_info": SecurityLevel.CONFIDENTIAL,       # 用户信息
        "payment_records": SecurityLevel.SECRET,       # 支付记录
        "employee_data": SecurityLevel.CONFIDENTIAL,   # 员工数据
        "public_reports": SecurityLevel.PUBLIC,        # 公开报告
    }
    
    # 从配置加载自定义敏感表
    if hasattr(self.config, 'get'):
        config_tables = self.config.get("sensitive_tables", {})
        for table_name, level in config_tables.items():
            if isinstance(level, str):
                try:
                    default_tables[table_name] = SecurityLevel(level.lower())
                except ValueError:
                    default_tables[table_name] = SecurityLevel.INTERNAL
            else:
                default_tables[table_name] = level
    
    return default_tables
```

### 7.3 脱敏规则定义

```python
@dataclass
class MaskingRule:
    """数据脱敏规则"""
    
    column_pattern: str        # 列名正则匹配
    algorithm: str            # 脱敏算法
    parameters: dict          # 算法参数
    security_level: SecurityLevel  # 生效的安全级别

# 默认脱敏规则
default_rules = [
    MaskingRule(
        column_pattern=r".*phone.*|.*mobile.*",
        algorithm="phone_mask",
        parameters={"mask_char": "*", "keep_prefix": 3, "keep_suffix": 4},
        security_level=SecurityLevel.INTERNAL,
    ),
    MaskingRule(
        column_pattern=r".*email.*",
        algorithm="email_mask",
        parameters={"mask_char": "*"},
        security_level=SecurityLevel.INTERNAL,
    ),
    MaskingRule(
        column_pattern=r".*id_card.*|.*identity.*",
        algorithm="id_mask",
        parameters={"mask_char": "*", "keep_prefix": 6, "keep_suffix": 4},
        security_level=SecurityLevel.CONFIDENTIAL,
    ),
]
```

### 7.4 脱敏处理流程

```python
async def apply_data_masking(
    self, data: list[dict[str, Any]], auth_context: AuthContext
) -> list[dict[str, Any]]:
    """应用数据脱敏处理"""
    
    # 根据用户安全级别确定是否需要脱敏
    if auth_context.security_level == SecurityLevel.PUBLIC:
        # 公开级别用户看到的全部脱敏
        return self._apply_full_masking(data)
    
    # 确定适用的脱敏规则
    applicable_rules = self._get_applicable_rules(auth_context.security_level)
    
    # 对每条记录应用脱敏规则
    masked_data = []
    for row in data:
        masked_row = {}
        for column, value in row.items():
            masked_row[column] = self._apply_column_masking(
                column, value, auth_context.security_level, applicable_rules
            )
        masked_data.append(masked_row)
    
    return masked_data

def _apply_column_masking(
    self,
    column: str,
    value: Any,
    security_level: SecurityLevel,
    rules: list[MaskingRule]
) -> Any:
    """对单个列应用脱敏"""
    
    # 如果值已经是脱敏的，直接返回
    if self._is_already_masked(value):
        return value
    
    # 查找适用的规则
    for rule in rules:
        if re.match(rule.column_pattern, column, re.IGNORECASE):
            return self._execute_masking_algorithm(value, rule.algorithm, rule.parameters)
    
    # 如果没有匹配的规则，根据安全级别决定是否脱敏
    if security_level == SecurityLevel.INTERNAL:
        # 内部级别：默认脱敏敏感类型数据
        if self._is_sensitive_data_type(column):
            return self._default_mask(value)
    
    return value

def _execute_masking_algorithm(
    self, value: Any, algorithm: str, parameters: dict
) -> str:
    """执行脱敏算法"""
    value_str = str(value) if value is not None else ""
    
    if algorithm == "phone_mask":
        return self._mask_phone(value_str, **parameters)
    elif algorithm == "email_mask":
        return self._mask_email(value_str, **parameters)
    elif algorithm == "id_mask":
        return self._mask_id_card(value_str, **parameters)
    elif algorithm == "name_mask":
        return self._mask_name(value_str, **parameters)
    elif algorithm == "custom_mask":
        return self._custom_mask(value_str, **parameters)
    else:
        return self._default_mask(value_str)

def _mask_phone(self, phone: str, mask_char: str = "*", keep_prefix: int = 3, keep_suffix: int = 4) -> str:
    """手机号脱敏"""
    if len(phone) < keep_prefix + keep_suffix:
        return mask_char * len(phone)
    
    prefix = phone[:keep_prefix]
    suffix = phone[-keep_suffix:]
    middle_length = len(phone) - keep_prefix - keep_suffix
    middle = mask_char * middle_length
    
    return f"{prefix}{middle}{suffix}"

def _mask_email(self, email: str, mask_char: str = "*") -> str:
    """邮箱脱敏"""
    if "@" not in email:
        return mask_char * len(email)
    
    local, domain = email.split("@", 1)
    
    if len(local) <= 2:
        masked_local = mask_char * len(local)
    else:
        masked_local = local[0] + mask_char * (len(local) - 1)
    
    return f"{masked_local}@{domain}"

def _mask_id_card(self, id_card: str, mask_char: str = "*", keep_prefix: int = 6, keep_suffix: int = 4) -> str:
    """身份证号脱敏"""
    if len(id_card) < keep_prefix + keep_suffix:
        return mask_char * len(id_card)
    
    prefix = id_card[:keep_prefix]
    suffix = id_card[-keep_suffix:]
    middle_length = len(id_card) - keep_prefix - keep_suffix
    middle = mask_char * middle_length
    
    return f"{prefix}{middle}{suffix}"
```

### 7.5 数据脱敏处理器

```python
class DataMaskingProcessor:
    """数据脱敏处理器"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        
        # 加载脱敏规则
        self.masking_rules = self._load_masking_rules()
    
    async def process(
        self, data: list[dict[str, Any]], auth_context: AuthContext
    ) -> list[dict[str, Any]]:
        """处理数据脱敏"""
        try:
            # 根据用户角色确定脱敏级别
            security_level = self._determine_security_level(auth_context)
            
            # 应用脱敏规则
            masked_data = []
            for row in data:
                masked_row = self._mask_row(row, security_level)
                masked_data.append(masked_row)
            
            return masked_data
            
        except Exception as e:
            self.logger.error(f"Data masking failed: {e}")
            # 脱敏失败时返回原始数据或空数据
            return data
    
    def _determine_security_level(self, auth_context: AuthContext) -> SecurityLevel:
        """确定用户的安全级别"""
        if "admin" in auth_context.roles:
            return SecurityLevel.PUBLIC
        elif "analyst" in auth_context.roles:
            return SecurityLevel.INTERNAL
        elif "readonly" in auth_context.roles:
            return SecurityLevel.INTERNAL
        else:
            return SecurityLevel.CONFIDENTIAL
```

## 8. Token 生命周期管理

### 8.1 Token 创建

```python
async def create_token(
    self,
    token_id: str,
    expires_hours: Optional[int] = None,
    description: str = "",
    custom_token: Optional[str] = None,
    database_config: Optional[DatabaseConfig] = None
) -> str:
    """创建新的 API 访问 Token
    
    Args:
        token_id: Token 的唯一标识，用于审计和管理
        expires_hours: Token 过期时间（小时），None 表示永不过期
        description: Token 的描述信息
        custom_token: 自定义 Token 字符串（如果为 None，则生成随机 Token）
        database_config: 此 Token 的可选数据库配置
        
    Returns:
        生成的 Token 字符串
    """
    if not self.auth_provider.token_manager:
        raise ValueError("Token manager not initialized")
    
    # 1. 验证数据库配置连通性
    await self._validate_token_database_config(token, token_info)
    
    # 2. 生成或使用自定义 Token
    if custom_token:
        token = custom_token
    else:
        token = self._generate_secure_token()
    
    # 3. 存储 Token 信息（包含数据库配置）
    token_info = TokenInfo(
        token_id=token_id,
        token=token,
        created_at=datetime.utcnow(),
        expires_hours=expires_hours,
        description=description,
        database_config=database_config  # 绑定数据库配置
    )
    
    # 4. 持久化存储
    await self.token_manager._persist_tokens()
    
    return token

def _generate_secure_token(self) -> str:
    """生成安全的随机 Token"""
    import secrets
    import string
    
    # 生成 32 字符的随机 Token
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    
    return f"doris_{token}"
```

### 8.2 Token 绑定数据库配置

这是系统的核心安全特性之一：

```python
async def _validate_token_database_config(self, token: str, token_info):
    """验证 Token 绑定的数据库配置
    
    在认证时立即验证数据库配置，确保数据库连接问题在认证阶段被发现，
    而不是等到查询执行时，提供更好的用户体验。
    
    Args:
        token: 原始认证 Token
        token_info: Token 验证后的 TokenInfo 对象
        
    Raises:
        ValueError: 如果数据库配置无效或连接失败
    """
    try:
        if not self.connection_manager:
            self.logger.warning("Connection manager not available for immediate database validation")
            return
        
        # 配置并测试数据库连接
        success, config_source = await self.connection_manager.configure_for_token(token)
        
        if success:
            self.logger.info(
                f"Database configuration validated successfully for token {token_info.token_id} "
                f"(source: {config_source})"
            )
        else:
            raise ValueError("Database configuration validation failed")
            
    except Exception as e:
        error_msg = f"Database configuration validation failed for token {token_info.token_id}: {str(e)}"
        self.logger.error(error_msg)
        raise ValueError(error_msg)
```

### 8.3 Token 撤销

```python
async def revoke_token(self, token_id: str) -> bool:
    """撤销 Token
    
    Args:
        token_id: 要撤销的 Token ID
        
    Returns:
        如果 Token 成功撤销则返回 True
    """
    if not self.auth_provider.token_manager:
        raise ValueError("Token manager not initialized")
    
    # 检查 Token 是否存在
    token_info = await self.token_manager.get_token_info(token_id)
    if not token_info:
        self.logger.warning(f"Attempt to revoke non-existent token: {token_id}")
        return False
    
    # 执行撤销
    await self.token_manager.revoke_token_by_id(token_id)
    
    # 清除该 Token 的缓存配置
    await self.connection_manager.clear_token_config(token_info.token)
    
    self.logger.info(f"Token revoked successfully: {token_id}")
    return True
```

### 8.4 Token 过期清理

```python
async def cleanup_expired_tokens(self) -> int:
    """清理过期的 Token
    
    Returns:
        清理的过期 Token 数量
    """
    if not self.auth_provider.token_manager:
        return 0
    
    # 获取所有 Token
    tokens = await self.token_manager.list_tokens()
    
    # 找出过期的 Token
    expired_count = 0
    current_time = datetime.utcnow()
    
    for token in tokens:
        if token.get("expires_at"):
            expires_at = datetime.fromisoformat(token["expires_at"])
            if expires_at < current_time:
                await self.token_manager.revoke_token_by_id(token["token_id"])
                expired_count += 1
    
    self.logger.info(f"Cleaned up {expired_count} expired tokens")
    return expired_count
```

### 8.5 Token 统计

```python
def get_token_stats(self) -> dict[str, Any]:
    """获取 Token 统计信息"""
    if not self.auth_provider.token_manager:
        return {"error": "Token manager not initialized"}
    
    tokens = self.token_manager._load_tokens()
    
    total = len(tokens)
    active = sum(1 for t in tokens if t.get("is_active", True))
    expired = sum(1 for t in tokens if self._is_expired(t))
    
    return {
        "total_tokens": total,
        "active_tokens": active,
        "expired_tokens": expired,
        "expiry_enabled": self.token_manager.default_expiry_hours is not None,
        "default_expiry_hours": self.token_manager.default_expiry_hours
    }
```

## 9. 审计日志与监控

### 9.1 认证审计

每次认证请求都会记录详细日志：

```python
async def authenticate_request(self, auth_info: dict[str, Any]) -> AuthContext:
    """认证请求审计"""
    
    client_ip = auth_info.get("client_ip", "unknown")
    auth_method = self._get_auth_method(auth_info)
    
    # 记录认证尝试
    self.logger.info(f"Authentication attempt from {client_ip} via {auth_method}")
    
    try:
        # 执行认证逻辑
        auth_context = await self._do_authenticate(auth_info)
        
        # 认证成功日志
        self.logger.info(
            f"Authentication successful for {auth_context.user_id} "
            f"(token_id: {auth_context.token_id}, "
            f"roles: {auth_context.roles}, "
            f"security_level: {auth_context.security_level.value})"
        )
        
        return auth_context
        
    except Exception as e:
        # 认证失败告警
        self.logger.warning(
            f"Authentication failed for client {client_ip}: {str(e)}"
        )
        raise
```

### 9.2 Tool 执行审计

Tool 调用记录完整的执行信息：

```python
async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
    """Tool 执行审计"""
    try:
        start_time = time.time()
        
        # 记录工具调用开始
        self.logger.info(f"Tool call started: {name}")
        self.logger.debug(f"Tool arguments: {arguments}")
        
        # 执行 Tool
        result = await self._execute_tool(name, arguments)
        
        execution_time = time.time() - start_time
        
        # 记录执行结果
        self.logger.info(
            f"Tool call completed: {name} "
            f"(execution_time: {execution_time:.3f}s)"
        )
        
        # 添加执行信息到结果
        if isinstance(result, dict):
            result["_execution_info"] = {
                "tool_name": name,
                "execution_time": round(execution_time, 3),
                "timestamp": datetime.now().isoformat(),
            }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        self.logger.error(f"Tool call failed {name}: {str(e)}")
        
        # 错误审计
        error_result = {
            "error": str(e),
            "tool_name": name,
            "arguments": arguments,
            "timestamp": datetime.now().isoformat(),
        }
        
        # 记录详细的错误信息
        self.logger.error(
            f"Tool execution error: {name}, "
            f"error: {str(e)}, "
            f"args: {arguments}"
        )
        
        return json.dumps(error_result, ensure_ascii=False, indent=2)
```

### 9.3 SQL 执行审计

```python
async def exec_query_for_mcp(
    self, sql: str, db_name: str = None, catalog_name: str = None,
    max_rows: int = 100, timeout: int = 30
) -> Dict[str, Any]:
    """SQL 执行审计"""
    
    # SQL 执行前审计
    self.logger.info(
        f"SQL execution started "
        f"(user: {self.current_user}, "
        f"db: {db_name}, "
        f"catalog: {catalog_name}, "
        f"max_rows: {max_rows})"
    )
    
    # 记录 SQL 内容（脱敏后）
    sanitized_sql = self._sanitize_sql_for_logging(sql)
    self.logger.debug(f"SQL query: {sanitized_sql}")
    
    try:
        # 执行 SQL
        result = await self._actual_query_execution(sql, db_name, catalog_name, max_rows, timeout)
        
        # 执行成功审计
        self.logger.info(
            f"SQL execution completed "
            f"(rows_returned: {len(result.get('data', []))}, "
            f"execution_time: {result.get('execution_time', 'N/A')}s)"
        )
        
        return result
        
    except Exception as e:
        # 执行失败审计
        self.logger.error(
            f"SQL execution failed "
            f"(error: {str(e)}, "
            f"query: {sanitized_sql})"
        )
        raise
```

### 9.4 安全事件审计

```python
class SecurityAuditLogger:
    """安全审计日志记录器"""
    
    def __init__(self):
        self.logger = get_logger("security_audit")
    
    def log_auth_event(self, event_type: str, auth_context: AuthContext, success: bool, details: dict = None):
        """记录认证事件"""
        event_data = {
            "event_type": event_type,
            "user_id": auth_context.user_id,
            "token_id": auth_context.token_id,
            "client_ip": auth_context.client_ip,
            "session_id": auth_context.session_id,
            "roles": auth_context.roles,
            "security_level": auth_context.security_level.value,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if details:
            event_data["details"] = details
        
        if success:
            self.logger.info(f"Auth event: {json.dumps(event_data)}")
        else:
            self.logger.warning(f"Auth event failed: {json.dumps(event_data)}")
    
    def log_permission_denied(self, auth_context: AuthContext, resource: str, operation: str):
        """记录权限拒绝事件"""
        event_data = {
            "event_type": "permission_denied",
            "user_id": auth_context.user_id,
            "token_id": auth_context.token_id,
            "client_ip": auth_context.client_ip,
            "resource": resource,
            "operation": operation,
            "roles": auth_context.roles,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.warning(f"Permission denied: {json.dumps(event_data)}")
    
    def log_security_violation(self, violation_type: str, details: dict):
        """记录安全违规事件"""
        event_data = {
            "event_type": "security_violation",
            "violation_type": violation_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.error(f"Security violation: {json.dumps(event_data)}")
```

## 10. 安全配置最佳实践

### 10.1 认证配置说明

**重要说明**：多个认证开关之间是"或"逻辑，不是"与"逻辑。

系统按优先级顺序尝试认证方法：**Token → JWT → OAuth**，任意一种方法成功即可访问。

这种设计支持**渐进式迁移**：
1. **初期**：所有用户使用 Token 认证
2. **迁移期**：启用 JWT，新用户用 JWT，老用户继续用 Token
3. **最终**：关闭 Token，全面切换到 JWT

### 10.2 生产环境配置建议

```bash
# ============================================
# 安全认证配置 - 选择其中一种即可
# ============================================

# 场景1：简单场景 - 只用 Token（推荐）
ENABLE_TOKEN_AUTH=true
ENABLE_JWT_AUTH=false
ENABLE_OAUTH_AUTH=false

# 场景2：企业级 - 只用 JWT
# ENABLE_TOKEN_AUTH=false
# ENABLE_JWT_AUTH=true
# ENABLE_OAUTH_AUTH=false

# 场景3：混合场景 - Token + JWT（用于迁移期）
# ENABLE_TOKEN_AUTH=true
# ENABLE_JWT_AUTH=true
# ENABLE_OAUTH_AUTH=false

# Token 安全配置
TOKEN_SECRET_KEY=your-production-secret-key-change-this

# JWT 配置（如果启用 JWT）
# JWT_ALGORITHM=RS256
# JWT_EXPIRATION_HOURS=24

# ============================================
# HTTP Token 管理安全配置
# ============================================

# 生产环境关闭 HTTP Token 管理
ENABLE_HTTP_TOKEN_MANAGEMENT=false

# 如果需要启用，严格限制 IP
ALLOWED_TOKEN_MANAGEMENT_IPS=127.0.0.1,10.0.0.1

# ============================================
# SQL 安全配置
# ============================================

# 危险操作关键字拦截
BLOCKED_KEYWORDS=DROP,CREATE,ALTER,TRUNCATE,DELETE,INSERT,UPDATE,GRANT,REVOKE,EXEC,EXECUTE,SHUTDOWN,KILL

# ============================================
# 数据脱敏配置
# ============================================

# 敏感表配置
SENSITIVE_TABLES={"financial_records": "secret", "personal_data": "secret", "user_profiles": "confidential"}

# 脱敏规则
MASKING_RULES=[{"column_pattern": ".*password.*", "algorithm": "full_mask", "security_level": "internal"}]
```

### 10.3 敏感表保护策略

```python
# 敏感表分级保护配置
SENSITIVE_TABLES = {
    # 绝密级：完全禁止访问或强脱敏
    "financial_records": SecurityLevel.SECRET,
    "personal_data": SecurityLevel.SECRET,
    "salary_data": SecurityLevel.SECRET,
    
    # 机密级：严格脱敏
    "user_profiles": SecurityLevel.CONFIDENTIAL,
    "order_history": SecurityLevel.CONFIDENTIAL,
    "transaction_records": SecurityLevel.CONFIDENTIAL,
    
    # 内部级：基础脱敏
    "internal_logs": SecurityLevel.INTERNAL,
    "audit_trail": SecurityLevel.INTERNAL,
    "system_config": SecurityLevel.INTERNAL,
    
    # 公开级：无脱敏
    "public_reports": SecurityLevel.PUBLIC,
    "product_catalog": SecurityLevel.PUBLIC,
}
```

### 10.4 访问控制矩阵

| 用户角色 | exec_query | get_table_schema | get_db_table_list |
|---------|-----------|------------------|-------------------|
| admin | ✅ 全部（允许写操作） | ✅ 全部 | ✅ 全部 |
| analyst | ✅ 只读 | ✅ 全部 | ✅ 全部 |
| readonly | ✅ 只读 | ✅ 全部 | ✅ 全部 |
| anonymous | ❌ 拒绝 | ✅ 全部 | ✅ 全部 |

### 10.5 Token 管理最佳实践

```python
# Token 管理建议

# 1. 为不同用途创建不同的 Token
tokens = [
    {
        "token_id": "production-readonly",
        "description": "生产环境只读访问",
        "permissions": ["read"],
        "expires_hours": 720  # 30天
    },
    {
        "token_id": "development-full",
        "description": "开发环境完全访问",
        "permissions": ["read", "write"],
        "expires_hours": 168  # 7天
    },
    {
        "token_id": "admin-operations",
        "description": "管理员操作",
        "permissions": ["read", "write", "admin"],
        "expires_hours": 24  # 1天
    }
]

# 2. 定期轮换 Token
# 建议每 90 天轮换一次生产环境 Token

# 3. 及时撤销不需要的 Token
# 员工离职、项目结束等情况需要立即撤销

# 4. 使用强 Token
# 避免使用简单可猜测的 Token 值
```

### 10.6 监控告警配置

```python
# 安全监控告警建议

# 1. 认证失败告警
# 当同一 IP 在 5 分钟内认证失败超过 10 次时触发告警

# 2. 异常访问告警
# 当用户尝试访问未授权资源时触发告警

# 3. SQL 安全拦截告警
# 当 SQL 被安全拦截时记录并告警

# 4. Token 异常告警
# 当 Token 使用模式异常（如大量查询、异常时间访问）时触发告警

SECURITY_ALERTS = {
    "auth_failure_threshold": 10,
    "auth_failure_window_minutes": 5,
    "unauthorized_access_alert": True,
    "sql_blocked_alert": True,
    "token_anomaly_alert": True
}
```

## 11. 安全架构总结

Doris MCP Server 的安全架构通过以下核心机制提供全面保护：

### 11.1 多层防护体系

1. **边界安全**：IP 白名单、认证中间件
2. **身份认证**：Token、JWT、OAuth 多认证机制
3. **权限控制**：基于角色的细粒度访问控制
4. **SQL 安全**：危险操作拦截、SQL 注入防护
5. **数据保护**：多级脱敏、敏感数据分类
6. **审计追踪**：完整的操作审计和日志记录

### 11.2 核心安全特性

- **Token 绑定数据库配置**：每个 Token 可配置独立的数据库连接，实现数据源隔离
- **灵活的认证策略**：支持多种认证方式的任意组合
- **细粒度权限控制**：基于角色、资源、操作的多维度权限管理
- **智能数据脱敏**：根据用户角色和数据敏感度自动应用脱敏规则
- **完整的审计能力**：记录所有安全相关事件，便于追溯和监控

### 11.3 安全配置清单

- [ ] 启用强认证机制（Token 或 JWT）
- [ ] 配置 Token 过期策略
- [ ] 设置敏感表分级保护
- [ ] 配置数据脱敏规则
- [ ] 启用 SQL 安全校验
- [ ] 配置审计日志
- [ ] 设置监控告警
- [ ] 定期轮换和清理 Token

该安全架构通过多层次的防护机制，确保了 Doris MCP Server 在各种部署场景下的安全性，同时保持了良好的可用性和扩展性。
