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

### 3.5 令牌认证

### 3.5.1 令牌认证概述

令牌认证是 Doris MCP Server 最基础、最常用的认证方式，适用于简单的 API 访问场景。用户通过预先配置的令牌（Token）访问 MCP Server，令牌与数据库连接配置绑定，实现了**令牌即身份+令牌即权限**的设计理念。

### 3.5.2 令牌配置文件结构

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
    },
    {
      "token_id": "analyst-token",
      "token": "doris_analyst_token_654321",
      "description": "Data analyst access token",
      "expires_hours": 720,
      "is_active": true,
      "database_config": {
        "host": "127.0.0.1",
        "port": 9030,
        "user": "analyst",
        "password": "analyst_pass",
        "database": "analytics_db",
        "charset": "UTF8",
        "fe_http_port": 8030
      }
    }
  ]
}
```

**令牌配置说明**：

| 字段 | 说明 | 示例 |
|------|------|------|
| `token_id` | 令牌唯一标识符 | "admin-token" |
| `token` | 令牌值（用于认证） | "doris_admin_token_123456" |
| `description` | 令牌描述 | "Doris admin API access token" |
| `expires_hours` | 有效期（小时），null 表示永不过期 | null, 720 |
| `is_active` | 是否激活 | true, false |
| `database_config` | 绑定的数据库连接配置 | {...} |

### 3.5.3 令牌管理 API

在 HTTP 模式下，TokenHandlers 提供了完整的令牌管理端点：

| 端点 | 方法 | 功能 | 访问控制 |
|------|------|------|---------|
| `/token/create` | GET/POST | 创建新令牌 | 仅 localhost |
| `/token/revoke/{token_id}` | DELETE | 撤销指定令牌 | 仅 localhost |
| `/token/list` | GET | 列出所有令牌 | 仅 localhost |
| `/token/stats` | GET | 获取令牌统计信息 | 仅 localhost |
| `/token/cleanup` | POST | 清理过期令牌 | 仅 localhost |

**创建令牌示例**：

```bash
# 通过查询参数创建令牌
curl -X GET "http://localhost:8000/token/create?token_id=my-token&expires_hours=24&description=My+API+Token"

# 通过 JSON Body 创建令牌（支持数据库配置）
curl -X POST "http://localhost:8000/token/create" \
  -H "Content-Type: application/json" \
  -d '{
    "token_id": "my-token",
    "expires_hours": 24,
    "description": "My API Token",
    "database_config": {
      "host": "127.0.0.1",
      "port": 9030,
      "user": "myuser",
      "password": "mypassword",
      "database": "mydb"
    }
  }'
```

**响应示例**：

```json
{
  "success": true,
  "token_id": "my-token",
  "token": "doris_my_token_abc123def456",
  "expires_hours": 24,
  "description": "My API Token",
  "message": "Token created successfully"
}
```

### 3.5.4 令牌认证流程

```python
async def authenticate_token(self, auth_info: dict[str, Any]) -> AuthContext:
    """令牌认证方法"""
    
    # 1. 提取令牌
    token = auth_info.get("token", "")
    if not token:
        # 尝试从 Authorization header 提取
        auth_header = auth_info.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    if not token:
        raise ValueError("No token provided")
    
    # 2. 验证令牌
    token_data = await self.token_manager.validate_token(token)
    if not token_data:
        raise ValueError("Invalid or expired token")
    
    # 3. 获取数据库配置（令牌绑定）
    db_config = token_data.get("database_config")
    
    # 4. 创建认证上下文
    auth_context = AuthContext(
        token_id=token_data.get("token_id"),
        user_id=token_data.get("token_id"),  # 使用 token_id 作为用户标识
        roles=["token_user"],
        permissions=["read", "execute_query"],
        security_level=SecurityLevel.INTERNAL,
        client_ip=auth_info.get("client_ip", "unknown"),
        session_id=str(uuid.uuid4()),
        token=token  # 保存原始令牌用于绑定数据库配置
    )
    
    return auth_context
```

### 3.5.5 使用令牌访问 MCP Server

```bash
# 方式一：直接传递令牌
curl -X POST "http://localhost:8000/mcp/call" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer doris_admin_token_123456" \
  -d '{
    "tool": "exec_query",
    "arguments": {
      "sql": "SELECT * FROM internal.information_schema.tables LIMIT 10"
    }
  }'

# 方式二：在请求体中传递令牌
curl -X POST "http://localhost:8000/mcp/call" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "doris_admin_token_123456",
    "tool": "exec_query",
    "arguments": {
      "sql": "SELECT * FROM internal.information_schema.tables LIMIT 10"
    }
  }'
```

## 3.6 JWT 认证

### 3.6.1 JWT 认证概述

JWT（JSON Web Token）认证是一种**无状态**的认证方式，适用于分布式系统和微服务架构。JWT 令牌包含用户身份信息和声明（Claims），服务端可以自行验证令牌有效性，无需维护会话状态。

Doris MCP Server 的 JWT 认证支持：

- **多种签名算法**：HS256、RS256、ES256
- **双令牌机制**：Access Token + Refresh Token
- **令牌黑名单**：支持令牌主动撤销
- **密钥轮换**：自动化的密钥更新机制
- **完整的声明验证**：issuer、audience、expiration 等

### 3.6.2 JWT 配置

在 `.env` 文件中配置 JWT 认证参数：

```bash
# 启用 JWT 认证
ENABLE_JWT_AUTH=true

# JWT 签名算法（HS256 对称加密，RS256/ES256 非对称加密）
JWT_ALGORITHM=RS256

# JWT 密钥配置
# 对于 HS256：使用 JWT_SECRET_KEY
# 对于 RS256/ES256：使用密钥文件路径
JWT_SECRET_KEY=your_hs256_secret_key_here
JWT_PRIVATE_KEY_PATH=./keys/jwt_private.pem
JWT_PUBLIC_KEY_PATH=./keys/jwt_public.pem

# JWT 令牌发行者
JWT_ISSUER=doris-mcp-server

# JWT 令牌受众
JWT_AUDIENCE=doris-mcp-client

# Access Token 有效期（秒）
JWT_ACCESS_TOKEN_EXPIRY=3600

# Refresh Token 有效期（秒）
JWT_REFRESH_TOKEN_EXPIRY=604800

# 令牌验证开关
JWT_VERIFY_SIGNATURE=true
JWT_VERIFY_EXPIRATION=true
JWT_VERIFY_AUDIENCE=true
JWT_VERIFY_ISSUER=true

# 时钟偏差容忍（秒）
JWT_LEEWAY=10
```

### 3.6.3 JWT 令牌结构

JWT 令牌由三部分组成：`header.payload.signature`

**Header（头部）**：

```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

**Payload（载荷）**：

```json
{
  "iss": "doris-mcp-server",
  "aud": "doris-mcp-client",
  "sub": "user123",
  "iat": 1704067200,
  "exp": 1704070800,
  "jti": "550e8400-e29b-41d4-a716-446655440000",
  "roles": ["admin", "analyst"],
  "permissions": ["read", "write", "execute_query"],
  "security_level": "internal"
}
```

**Claims 说明**：

| Claim | 说明 | 必填 |
|-------|------|------|
| `iss` (issuer) | 令牌发行者 | 是 |
| `aud` (audience) | 令牌受众 | 是 |
| `sub` (subject) | 用户标识 | 是 |
| `iat` (issued at) | 发行时间 | 可选 |
| `exp` (expiration time) | 过期时间 | 可选 |
| `jti` (JWT ID) | 令牌唯一标识 | 可选 |
| `roles` | 用户角色列表 | 可选 |
| `permissions` | 用户权限列表 | 可选 |
| `security_level` | 安全级别 | 可选 |

### 3.6.4 JWT 令牌生成

```python
from doris_mcp_server.auth.jwt_manager import JWTManager

async def generate_jwt_tokens():
    """生成 JWT 令牌对"""
    
    jwt_manager = JWTManager(config)
    
    # 用户信息
    user_info = {
        "user_id": "user123",
        "roles": ["admin", "analyst"],
        "permissions": ["read", "write", "execute_query"],
        "security_level": "internal"
    }
    
    # 生成令牌
    tokens = await jwt_manager.generate_tokens(user_info)
    
    return tokens
```

**返回结果**：

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_expires_in": 604800,
  "user_id": "user123",
  "issued_at": 1704067200
}
```

### 3.6.5 JWT 令牌验证

```python
async def validate_jwt_token(token: str) -> dict:
    """验证 JWT 令牌"""
    
    jwt_manager = JWTManager(config)
    
    # 验证并解析令牌
    result = await jwt_manager.validate_token(token, token_type='access')
    
    if result["valid"]:
        return {
            "valid": True,
            "user_id": result["payload"].get("sub"),
            "roles": result["payload"].get("roles", []),
            "permissions": result["payload"].get("permissions", []),
            "security_level": result["payload"].get("security_level"),
            "payload": result["payload"]
        }
    else:
        return {
            "valid": False,
            "error": result.get("error", "Token validation failed")
        }
```

### 3.6.6 JWT 令牌刷新

```python
async def refresh_jwt_tokens(refresh_token: str):
    """使用 Refresh Token 获取新的 Access Token"""
    
    jwt_manager = JWTManager(config)
    
    # 验证 Refresh Token
    result = await jwt_manager.validate_token(refresh_token, token_type='refresh')
    
    if result["valid"]:
        # 从 Refresh Token 中提取用户信息
        payload = result["payload"]
        user_info = {
            "user_id": payload.get("sub"),
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", []),
            "security_level": payload.get("security_level")
        }
        
        # 生成新的令牌对
        new_tokens = await jwt_manager.generate_tokens(user_info)
        return new_tokens
    else:
        raise ValueError("Invalid refresh token")
```

### 3.6.7 JWT 令牌撤销

```python
async def revoke_jwt_token(jti: str):
    """撤销 JWT 令牌"""
    
    jwt_manager = JWTManager(config)
    
    # 将 JTI 加入黑名单
    success = await jwt_manager.revoke_token_by_jti(jti)
    
    return success
```

### 3.6.8 JWT 密钥管理

对于非对称加密算法（RS256、ES256），需要管理密钥对：

```bash
# 生成 RSA 密钥对
openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem

# 生成 ECDSA 密钥对
openssl ecparam -name prime256v1 -genkey -noout -out ecdsa_private.pem
openssl ec -in ecdsa_private.pem -pubout -out ecdsa_public.pem
```

**密钥轮换配置**：

```python
# 自动轮换间隔（秒），0 表示禁用自动轮换
KEY_ROTATION_INTERVAL = 30 * 24 * 3600  # 30天

# 手动触发密钥轮换
async def rotate_jwt_keys():
    """手动轮换 JWT 密钥"""
    jwt_manager = JWTManager(config)
    await jwt_manager.key_manager.rotate_keys()
```

### 3.6.9 JWT 认证流程图

```
┌─────────┐                           ┌─────────────────┐
│  Client │                           │ MCP Server      │
└────┬────┘                           └────────┬────────┘
     │                                         │
     │  1. POST /auth/login (credentials)      │
     │────────────────────────────────────────>│
     │                                         │
     │                          2. Validate   │
     │                             credentials│
     │                                         │
     │  3. Generate tokens                     │
     │    (access + refresh)                  │
     │<────────────────────────────────────────│
     │                                         │
     │  4. Access API with access_token        │
     │    (Authorization: Bearer <token>)      │
     │────────────────────────────────────────>│
     │                                         │
     │                          5. Validate    │
     │                             JWT token   │
     │                                         │
     │  6. Return requested data               │
     │<────────────────────────────────────────│
     │                                         │
     │  7. Access token expired →              │
     │     Use refresh_token to get new token  │
     │────────────────────────────────────────>│
     │                                         │
     │  8. Generate new token pair             │
     │<────────────────────────────────────────│
```

## 3.7 OAuth 认证

### 3.7.1 OAuth 认证概述

OAuth 2.0 是一种开放标准授权协议，允许用户在不提供用户名和密码的情况下，让第三方应用访问其存储在其他服务提供者上的资源。Doris MCP Server 实现了简化的 OAuth 2.0 授权码流程，支持与企业身份管理系统（如 Keycloak、Auth0、Okta 等）集成。

### 3.7.2 OAuth 配置

在 `.env` 文件中配置 OAuth 参数：

```bash
# 启用 OAuth 认证
ENABLE_OAUTH_AUTH=true

# OAuth 提供者类型
OAUTH_PROVIDER=keycloak  # keycloak, auth0, okta, generic

# OAuth 客户端配置
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret

# OAuth 服务器配置
OAUTH_AUTH_URL=https://your-auth-server/realms/your-realm/protocol/openid-connect/auth
OAUTH_TOKEN_URL=https://your-auth-server/realms/your-realm/protocol/openid-connect/token
OAUTH_USERINFO_URL=https://your-auth-server/realms/your-realm/protocol/openid-connect/userinfo
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback

# OAuth 作用域
OAUTH_SCOPES=openid profile email

# PKCE 认证（增强安全性）
OAUTH_PKCE_ENABLED=true

# 令牌映射配置
OAUTH_TOKEN_MAP_ROLES=roles
OAUTH_TOKEN_MAP_PERMISSIONS=permissions
OAUTH_TOKEN_MAP_USER_ID=sub
```

### 3.7.3 OAuth 认证端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/auth/login` | GET | 发起 OAuth 登录 |
| `/auth/callback` | GET | OAuth 回调处理 |
| `/auth/provider` | GET | 获取 OAuth 提供者信息 |
| `/auth/demo` | GET | OAuth 演示页面 |

### 3.7.4 OAuth 登录流程

**步骤 1：发起登录**

```bash
curl -X GET "http://localhost:8000/auth/login"
```

**响应**：

```json
{
  "authorization_url": "https://your-auth-server/.../auth?client_id=xxx&redirect_uri=...&scope=openid+profile&state=xyz",
  "state": "xyz123",
  "provider": "keycloak",
  "message": "Navigate to authorization_url to complete OAuth login"
}
```

**步骤 2：用户授权**

用户访问返回的 `authorization_url`，在 OAuth 提供者页面完成身份验证和授权。

**步骤 3：处理回调**

OAuth 提供者将用户重定向到 `/auth/callback?code=xxx&state=xyz`：

```bash
curl -X GET "http://localhost:8000/auth/callback?code=authorization_code&state=xyz123"
```

**响应**：

```json
{
  "success": true,
  "user_id": "user123",
  "roles": ["admin", "analyst"],
  "permissions": ["read", "write"],
  "security_level": "internal",
  "session_id": "session-uuid",
  "message": "OAuth authentication successful"
}
```

### 3.7.5 OAuth 认证实现

```python
async def handle_oauth_callback(self, code: str, state: str) -> AuthContext:
    """处理 OAuth 回调"""
    
    # 1. 验证 state 防止 CSRF 攻击
    if not self._validate_state(state):
        raise ValueError("Invalid state parameter")
    
    # 2. 使用授权码交换访问令牌
    token_response = await self._exchange_code_for_token(code)
    
    # 3. 获取用户信息
    user_info = await self._get_user_info(token_response["access_token"])
    
    # 4. 从用户信息中提取角色和权限
    roles = self._extract_roles(user_info)
    permissions = self._extract_permissions(user_info)
    security_level = self._determine_security_level(user_info)
    
    # 5. 创建认证上下文
    auth_context = AuthContext(
        token_id=user_info.get("sub"),
        user_id=user_info.get("sub"),
        roles=roles,
        permissions=permissions,
        security_level=security_level,
        client_ip="oauth",
        session_id=str(uuid.uuid4())
    )
    
    return auth_context
```

### 3.7.6 OAuth 与 JWT 的集成

OAuth 认证成功后，可以颁发 JWT 令牌供后续 API 调用使用：

```python
async def oauth_login_flow(auth_code: str, state: str) -> dict:
    """完整的 OAuth 登录流程"""
    
    # 1. 处理 OAuth 回调，获取用户信息
    auth_context = await security_manager.handle_oauth_callback(auth_code, state)
    
    # 2. 生成 JWT 令牌
    user_info = {
        "user_id": auth_context.user_id,
        "roles": auth_context.roles,
        "permissions": auth_context.permissions,
        "security_level": auth_context.security_level.value
    }
    
    tokens = await jwt_manager.generate_tokens(user_info)
    
    return {
        "access_token": tokens["access_token"],
        "token_type": "Bearer",
        "expires_in": tokens["expires_in"],
        "refresh_token": tokens.get("refresh_token"),
        "user": {
            "user_id": auth_context.user_id,
            "roles": auth_context.roles
        }
    }
```

### 3.7.7 OAuth 演示页面

访问 `/auth/demo` 可以查看 OAuth 认证的交互式演示页面：

```bash
# 打开浏览器访问
http://localhost:8000/auth/demo
```

演示页面包含：
- OAuth 配置信息展示
- OAuth 登录按钮
- 认证结果展示
- API 端点说明

## 3.8 多认证方式对比

| 特性 | 令牌认证 | JWT 认证 | OAuth 认证 |
|------|---------|---------|-----------|
| **状态** | 有状态 | 无状态 | 无状态 |
| **复杂度** | 低 | 中 | 高 |
| **适用场景** | 简单 API | 分布式系统 | 企业集成 |
| **用户管理** | 外部 | 外部 | 外部 |
| **令牌刷新** | 需手动 | 自动 | 自动 |
| **安全性** | 中 | 高 | 高 |
| **单点登录** | 不支持 | 支持 | 支持 |
| **令牌撤销** | 即时 | 需黑名单 | 需黑名单 |**选择建议**：

- **令牌认证**：适用于简单的内部系统，令牌与数据库配置绑定
- **JWT 认证**：适用于分布式系统和微服务架构，需要无状态认证
- **OAuth 认证**：适用于企业环境，需要与现有身份管理系统集成

## 3.9 当前架构的局限性

### 3.9.1 多租户支持现状

Doris MCP Server 当前架构在多租户支持方面存在以下限制，需要在后续版本中改进：

| 限制项 | 当前状态 | 影响 |
|--------|---------|------|
| **连接池** | 单一全局连接池 | 无法为不同租户/用户维护独立的数据库连接 |
| **角色隔离** | 基于 Token 静态配置 | 角色和权限在 Token 级别，无法实现动态租户隔离 |
| **数据隔离** | 依赖数据库配置 | 虽然支持不同 Token 绑定不同数据库配置，但实际使用受限 |
| **会话管理** | 无状态设计 | 无法追踪租户会话上下文 |

### 3.9.2 多 Token 配置的局限性

虽然在 `tokens.json` 中可以配置多个 Token，每个 Token 可以绑定不同的数据库配置：

```json
{
  "tokens": [
    {
      "token_id": "tenant-a-admin",
      "token": "token_for_tenant_a",
      "database_config": {
        "host": "doris-a.example.com",
        "user": "tenant_a_user",
        "database": "tenant_a_db"
      }
    },
    {
      "token_id": "tenant-b-analyst",
      "token": "token_for_tenant_b",
      "database_config": {
        "host": "doris-b.example.com",
        "user": "tenant_b_user",
        "database": "tenant_b_db"
      }
    }
  ]
}
```

**但是存在以下问题**：

1. **单一连接池限制**
   ```
   当前架构：┌─────────────────────────────────────┐
             │        Doris MCP Server           │
             │  ┌─────────────────────────────┐  │
             │  │    全局单一连接池            │  │
             │  │  - 单个数据库连接实例        │  │
             │  │  - 共享连接池大小           │  │
             │  │  - 无法按租户隔离连接        │  │
             │  └─────────────────────────────┘  │
             └─────────────────────────────────────┘
   
   问题：
   - 所有请求共享同一个数据库连接池
   - 无法为不同租户维护独立的连接状态
   - 高并发时连接竞争激烈
   ```

2. **角色与权限的静态绑定**

   在 `security.py` 的 `authenticate_token` 方法中，Token 认证的 `AuthContext` 是硬编码的：

   ```python
   # /doris_mcp_server/utils/security.py 第 635-647 行
   return AuthContext(
       token_id=token_info.token_id,
       user_id=token_info.token_id,  # Use token_id as user_id for token auth
       roles=["token_user"],           # ⚠️ 所有 Token 都固定为这个角色
       permissions=["read", "write"],  # ⚠️ 所有 Token 都固定为这两个权限
       security_level=SecurityLevel.INTERNAL,  # ⚠️ 所有 Token 都是这个安全级别
       client_ip=auth_info.get("client_ip", "unknown"),
       session_id=auth_info.get("session_id", f"session_{token_info.token_id}"),
       login_time=datetime.utcnow(),
       last_activity=token_info.last_used,
       token=token  # Store raw token for token-bound database configuration
   )
   ```

   **这意味着**：即使在 `tokens.json` 中为不同的 Token 配置了不同的数据库连接，所有 Token 用户仍然获得完全相同的：
   - **角色**：`["token_user"]`
   - **权限**：`["read", "write"]`
   - **安全级别**：`INTERNAL`

   **无法实现**：
   - 为 Token A 配置 `["admin"]` 角色，为 Token B 配置 `["readonly"]` 角色
   - 为不同 Token 设置不同的权限集合
   - 基于 Token 的细粒度租户权限隔离
   - 不同租户使用不同的安全级别（如 `CONFIDENTIAL` vs `INTERNAL`）

   **对比 JWT 认证**：JWT 的 `generate_tokens` 方法支持从 `user_info` 中读取角色和权限：

   ```python
   # JWT 认证可以从 user_info 获取角色权限
   base_payload = {
       'sub': user_info.get('user_id'),
       'roles': user_info.get('roles', []),        # ✅ 从参数读取
       'permissions': user_info.get('permissions', []),  # ✅ 从参数读取
       'security_level': user_info.get('security_level', 'internal')  # ✅ 从参数读取
   }
   ```

   而 Token 认证无法做到这一点，这是两者在权限灵活性上的关键差异。

3. **无法实现真正的多租户隔离**
   ```
   场景：多租户 SaaS 应用
   
   期望架构：
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │  Tenant A   │    │  Tenant B   │    │  Tenant C   │
   │  User: Alice│    │  User: Bob  │    │  User: Carol│
   │  Role: Admin│    │  Role: User │    │  Role: Analyst│
   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                   ┌─────────────────┐
                   │  MCP Server     │
                   │  多租户隔离     │
                   │  - 租户ID追踪   │
                   │  - 角色动态分配 │
                   │  - 权限细粒度   │
                   └─────────────────┘
   
   当前架构限制：
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │  Tenant A   │    │  Tenant B   │    │  Tenant C   │
   │  token_aaa  │    │  token_bbb  │    │  token_ccc  │
   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                   ┌─────────────────┐
                   │  MCP Server     │
                   │  单连接池       │
                   │  无法隔离       │
                   └─────────────────┘
   ```

### 3.9.3 数据库配置绑定的实际限制

虽然 Token 支持绑定不同的 `database_config`：

```json
{
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
```

**但实际使用中存在以下问题**：

1. **运行时无法切换数据库配置**
   ```python
   # 当前实现：认证时确定数据库配置，后续无法更改
   async def authenticate_token(self, auth_info):
       token_data = await self.token_manager.validate_token(token)
       db_config = token_data.get("database_config")  # 认证时获取
       # 问题：整个请求生命周期都使用这个配置，无法动态切换
   ```

2. **连接池复用问题**
   ```python
   # 当前架构的问题
   async def execute_query(self, sql, auth_context):
       # 使用全局连接池，无法按租户隔离
       connection = await self.connection_pool.get_connection()
       # 所有租户共享连接池，无法追踪资源使用
   ```

3. **跨租户查询风险**
   ```sql
   -- 如果用户构造跨库查询，可能泄露数据
   SELECT * FROM internal.tenant_a_db.users
   JOIN internal.tenant_b_db.users ON ...
   
   -- 当前无法有效阻止这类跨租户访问
   ```

### 3.9.4 数据级别权限控制缺失

**核心问题**：当前三种认证方式（Token、JWT、OAuth）都只实现了**应用级别的权限控制**，完全没有**数据级别的权限控制**能力。

#### 三种认证方式的数据权限现状

| 认证方式 | 认证层面 | 应用级别权限 | 数据级别权限 |
|---------|---------|-------------|-------------|
| **Token** | ✅ 静态 Token | ❌ 硬编码固定 `["token_user"]` | ❌ 无 |
| **JWT** | ✅ 动态 Token | ✅ 从 `user_info` 读取 | ❌ 无 |
| **OAuth** | ✅ Provider 认证 | ✅ 从 Provider 回调获取 | ❌ 无 |

#### 什么是数据级别权限控制？

```
数据级别权限控制示例：

┌─────────────────────────────────────────────────────────────────┐
│                      用户 A (属于部门 Sales)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  应用级别权限：                                                   │
│  - 角色: ["analyst"]                                             │
│  - 权限: ["read", "execute_query"]                               │
│                                                                 │
│  数据级别权限：                                                   │
│  - 可访问数据库: sales_db                                         │
│  - 可访问表: orders, customers                                    │
│  - 可访问列: id, amount, region (排除: salary, bonus)            │
│  - 行级过滤: WHERE department = 'Sales'                          │
│                                                                 │
│  实际执行的 SQL：                                                 │
│  SELECT id, amount, region FROM sales_db.orders                 │
│  WHERE department = 'Sales'  -- 自动注入的行级过滤               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 当前架构缺少的关键能力

```python
# 当前架构：认证后直接执行用户查询，没有任何数据过滤
async def execute_query(self, sql, auth_context):
    # 问题：用户提交什么 SQL 就执行什么 SQL
    # 无法实现：
    # 1. 列级权限控制（隐藏敏感列）
    # 2. 行级权限控制（只返回用户有权访问的数据）
    # 3. 表级权限控制（限制只能访问授权的表）
    # 4. 数据库级权限控制（限制只能访问授权的数据库）
    
    result = await self.connection_manager.execute_query(
        query_request.session_id, 
        sql,  # 用户原始 SQL 直接执行
        query_request.parameters, 
        auth_context
    )
    return result
```

#### 数据级别权限控制的典型场景

| 场景 | 需求描述 | 当前架构支持 |
|------|---------|-------------|
| **列级安全** | 隐藏用户的工资、身份证号等敏感列 | ❌ 不支持 |
| **行级安全** | 用户只能查看自己部门/区域的数据 | ❌ 不支持 |
| **动态数据遮蔽** | 非授权用户看到的敏感数据显示为 `****` | ❌ 不支持 |
| **多租户数据隔离** | 每个租户只能访问自己的数据库/Schema | ⚠️ 部分支持（靠配置隔离） |
| **时间窗口控制** | 只能查询指定时间范围内的数据 | ❌ 不支持 |

#### 对比：三种认证方式的数据权限能力

**1. Token 认证**

```python
# security.py 认证实现
return AuthContext(
    token_id=token_info.token_id,
    user_id=token_info.token_id,
    roles=["token_user"],           # 固定角色
    permissions=["read", "write"],  # 固定权限
    # ❌ 缺少 data_policies 字段
    # ❌ 缺少 column_restrictions 字段  
    # ❌ 缺少 row_filters 字段
)
```

**2. JWT 认证**

```python
# jwt_manager.py 的 generate_tokens
base_payload = {
    'sub': user_info.get('user_id'),
    'roles': user_info.get('roles', []),
    'permissions': user_info.get('permissions', []),
    'security_level': user_info.get('security_level', 'internal')
    # ✅ 有 roles 和 permissions，但仅限于应用级别
    # ❌ 没有数据级别的访问控制策略
}
```

**3. OAuth 认证**

```python
# oauth_handlers.py 的 handle_callback
auth_context = AuthContext(
    user_id=user_info.get("user_id"),
    roles=id_token_claims.get("roles", []),
    permissions=id_token_claims.get("permissions", [])
    # ✅ 同样只有应用级别的角色权限
    # ❌ 没有数据级别的过滤策略
)
```

#### 实现数据级别权限控制的建议方案

**方案一：查询重写（Query Rewrite）**

```python
class DataLevelSecurityFilter:
    """数据级别安全过滤器"""
    
    async def filter_query(self, sql: str, auth_context) -> str:
        """根据用户权限重写查询"""
        filters = []
        
        # 1. 添加行级过滤
        row_policy = await self._get_row_policy(auth_context)
        if row_policy:
            filters.append(row_policy)
        
        # 2. 应用列级安全
        column_policy = await self._get_column_policy(auth_context)
        if column_policy:
            sql = self._apply_column_masking(sql, column_policy)
        
        # 3. 验证表访问权限
        tables = self._extract_tables(sql)
        for table in tables:
            if not await self._check_table_access(auth_context, table):
                raise PermissionError(f"Access denied to table: {table}")
        
        # 组合所有过滤条件
        if filters:
            sql = self._add_where_clause(sql, " AND ".join(filters))
        
        return sql
```

**方案二：基于策略的访问控制（PBAC）**

```python
# 扩展 AuthContext
@dataclass
class DataPolicy:
    """数据访问策略"""
    resource_type: str  # database, table, column, row
    resource_name: str  # 资源标识
    policy: str         # allow | deny
    conditions: Dict[str, Any]  # 策略条件
    masking: Optional[str] = None  # 数据遮蔽规则

@dataclass 
class ExtendedAuthContext(AuthContext):
    """扩展的认证上下文"""
    data_policies: List[DataPolicy] = field(default_factory=list)
    tenant_id: Optional[str] = None
    department_id: Optional[str] = None
    data_classification: str = "internal"
```

**方案三：数据库层面的行级安全（RLS）**

利用 Doris 的行级安全功能：

```sql
-- 创建行级安全策略
CREATE ROW POLICY sales_policy ON sales_db.orders
FOR SELECT
USING (department IN (
    SELECT department FROM user_departments WHERE user_id = current_user()
));
```

### 3.9.5 建议的改进方向

| 改进项 | 优先级 | 方案描述 |
|--------|--------|---------|
| **多连接池支持** | 高 | 为每个租户/用户维护独立的数据库连接池 |
| **动态租户上下文** | 高 | 在请求上下文中传递租户 ID，实现动态租户隔离 |
| **细粒度权限** | 中 | 实现基于用户而非 Token 的权限管理 |
| **行级数据过滤** | 中 | 根据租户 ID 自动添加数据过滤条件 |
| **审计日志** | 中 | 记录每个租户的操作日志 |

**改进后的架构示意**：

```
┌─────────────────────────────────────────────────────┐
│              Doris MCP Server (改进后)              │
│  ┌─────────────────────────────────────────────┐   │
│  │  租户上下文管理器                             │   │
│  │  - 解析请求中的租户标识                      │   │
│  │  - 加载租户配置                              │   │
│  │  - 管理租户会话                              │   │
│  └─────────────────────────────────────────────┘   │
│                          │                          │
│          ┌───────────────┼───────────────┐          │
│          ▼               ▼               ▼          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │  Tenant A   │ │  Tenant B   │ │  Tenant C   │   │
│  │  连接池     │ │  连接池     │ │  连接池     │   │
│  │  - 10连接   │ │  5连接      │ │  20连接     │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 3.9.5 当前架构适用场景

尽管存在多租户限制，当前架构仍然适用于以下场景：

| 场景 | 说明 | 推荐配置 |
|------|------|---------|
| **单租户内部系统** | 公司内部数据分析平台 | 令牌认证 + 单数据库 |
| **开发测试环境** | 开发、测试、预发布环境 | JWT 认证 + 测试数据库 |
| **简单 API 服务** | 对外提供简单查询 API | 令牌认证 + 只读用户 |
| **多实例部署** | 按租户部署独立 MCP Server 实例 | 每个实例独立配置 |

**不适用场景**：

- 需要严格多租户隔离的 SaaS 产品
- 租户数量动态变化的环境
- 需要细粒度租户级权限控制的场景
- 跨租户资源隔离有严格要求的场景

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
