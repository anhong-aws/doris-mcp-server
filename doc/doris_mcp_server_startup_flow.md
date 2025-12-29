# Doris MCP Server 启动流程与调用顺序分析

本文档详细分析 Apache Doris MCP Server 的启动流程、调用顺序和核心组件交互，基于 `main.py` 文件的实现。

## 1. 程序入口

### 1.1 同步主函数
```python
if __name__ == "__main__":
    main_sync()
```

### 1.2 异步主函数启动
```python
def main_sync():
    exit_code = asyncio.run(main())
    exit(exit_code)
```

## 2. 主函数流程 (`main()`) 分析

`main()` 函数是服务器的核心启动入口，负责配置加载、日志初始化和服务器启动：

### 2.1 配置加载
```python
# 从环境变量和.env文件加载配置
config = DorisConfig.from_env()

# 解析命令行参数并更新配置
update_configuration(config)
```

配置优先级：
- **命令行参数** > **环境变量** > **.env文件** > **默认值**

### 2.2 日志系统初始化
```python
from .utils.config import ConfigManager
config_manager = ConfigManager(config)
config_manager.setup_logging()

from .utils.logger import get_logger, log_system_info
logger = get_logger(__name__)
log_system_info()  # 记录系统信息用于调试
```

### 2.3 服务器实例创建
```python
server = DorisServer(config)
```

### 2.4 根据传输模式启动服务器
```python
if config.transport == "stdio":
    await server.start_stdio()
elif config.transport == "http":
    workers = getattr(config, 'workers', 1)
    if workers == 0:
        import multiprocessing
        workers = multiprocessing.cpu_count()
    await server.start_http(config.server_host, config.server_port, workers)
```

### 2.5 异常处理与资源清理
```python
try:
    # 服务器启动代码
    ...
except KeyboardInterrupt:
    logger.info("Received interrupt signal, shutting down server...")
except Exception as e:
    logger.error(f"Server runtime error: {e}")
    # 清理资源
    try:
        await server.shutdown()
    except Exception as shutdown_error:
        logger.error(f"Error occurred while shutting down server: {shutdown_error}")
    return 1
finally:
    # 正常关闭时的清理
    try:
        await server.shutdown()
    except Exception as shutdown_error:
        logger.error(f"Error occurred while shutting down server: {shutdown_error}")
    
    # 关闭日志系统
    from .utils.logger import shutdown_logging
    shutdown_logging()
```

## 3. DorisServer 初始化流程

### 3.1 核心组件初始化
```python
def __init__(self, config: DorisConfig):
    # 创建 MCP Server 实例
    self.server = Server("doris-mcp-server")

    # 初始化安全管理器
    self.security_manager = DorisSecurityManager(config)

    # 初始化连接管理器
    token_manager = self.security_manager.auth_provider.token_manager if hasattr(self.security_manager, 'auth_provider') and hasattr(self.security_manager.auth_provider, 'token_manager') else None
    self.connection_manager = DorisConnectionManager(config, self.security_manager, token_manager)
    
    # 设置连接管理器引用
    self.security_manager.connection_manager = self.connection_manager

    # 初始化独立管理器
    self.resources_manager = DorisResourcesManager(self.connection_manager)
    self.tools_manager = DorisToolsManager(self.connection_manager)
    self.prompts_manager = DorisPromptsManager(self.connection_manager)

    # 设置 MCP 协议处理器
    self._setup_handlers()
```

### 3.2 MCP 协议处理器设置 (`_setup_handlers()`)

```python
def _setup_handlers(self):
    # 资源列表请求处理
    @self.server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        resources = await self.resources_manager.list_resources()
        return resources

    # 资源读取请求处理
    @self.server.read_resource()
    async def handle_read_resource(uri: str) -> str:
        content = await self.resources_manager.read_resource(uri)
        return content

    # 工具列表请求处理
    @self.server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        tools = await self.tools_manager.list_tools()
        return tools

    # 工具调用请求处理
    @self.server.call_tool()
    async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        result = await self.tools_manager.call_tool(name, arguments)
        return [TextContent(type="text", text=result)]

    # 提示列表请求处理
    @self.server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        prompts = await self.prompts_manager.list_prompts()
        return prompts

    # 提示获取请求处理
    @self.server.get_prompt()
    async def handle_get_prompt(name: str, arguments: dict[str, Any]) -> str:
        result = await self.prompts_manager.get_prompt(name, arguments)
        return result
```

## 4. STDIO 模式启动流程 (`start_stdio()`)

STDIO 模式用于本地进程间通信，启动流程如下：

```python
async def start_stdio(self):
    # 初始化安全管理器
    await self.security_manager.initialize()
    
    # 建立数据库连接（STDIO模式专用初始化）
    await self.connection_manager.initialize_for_stdio_mode()

    # 导入并创建 stdio 服务器
    try:
        from mcp.server.stdio import stdio_server
    except ImportError:
        # 兼容不同 MCP 版本
        from mcp.server import stdio_server
    
    async with stdio_server() as streams:
        read_stream, write_stream = streams
        
        # 获取 MCP 能力
        capabilities = self._get_mcp_capabilities()
        
        # 创建初始化选项
        init_options = InitializationOptions(
            server_name="doris-mcp-server",
            server_version=os.getenv("SERVER_VERSION", _default_config.server_version),
            capabilities=capabilities,
        )
        
        # 运行 MCP 服务器
        await self.server.run(read_stream, write_stream, init_options)
```

## 5. HTTP 模式启动流程 (`start_http()`)

HTTP 模式提供网络访问能力，支持多进程部署，启动流程如下：

### 5.1 初始化核心组件
```python
# 初始化安全管理器
await self.security_manager.initialize()

# 初始化全局连接池（优雅降级）
global_pool_created = await self.connection_manager.initialize_for_http_mode()
```

### 5.2 创建 StreamableHTTP 会话管理器
```python
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
session_manager = StreamableHTTPSessionManager(
    app=self.server,
    json_response=True,
    stateless=False
)
```

### 5.3 设置 HTTP 端点

```python
# 健康检查端点
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "doris-mcp-server"})

# 连接池监控端点
from .monitor.pool_monitor_handlers import PoolMonitorHandlers
pool_monitor_handlers = PoolMonitorHandlers(self.connection_manager)

async def pool_monitor(request):
    return await pool_monitor_handlers.handle_pool_monitor(request)

# OAuth 端点
from .auth.oauth_handlers import OAuthHandlers
oauth_handlers = OAuthHandlers(self.security_manager)

async def oauth_login(request):
    return await oauth_handlers.handle_login(request)

# Token 管理端点
from .auth.token_handlers import TokenHandlers
token_handlers = TokenHandlers(self.security_manager, self.config)

async def token_create(request):
    return await token_handlers.handle_create_token(request)
```

### 5.4 创建 ASGI 应用

```python
async def mcp_app(scope, receive, send):
    # 处理生命周期事件
    if scope["type"] == "lifespan":
        await starlette_app(scope, receive, send)
        return
    
    # 处理 HTTP 请求
    if scope["type"] == "http":
        path = scope.get("path", "")
        
        # 处理健康检查、监控、认证等端点
        if (path.startswith("/health") or 
            path.startswith("/monitor/") or
            path.startswith("/auth/") or 
            path.startswith("/token/")):
            await starlette_app(scope, receive, send)
            return
        
        # 处理 MCP 请求
        if path == "/mcp" or path.startswith("/mcp/"):
            # 提取认证信息
            auth_info = await self._extract_auth_info_from_scope(scope, headers)
            
            # 认证请求
            auth_context = await self.security_manager.authenticate_request(auth_info)
            scope["auth_context"] = auth_context
            
            # 处理请求
            await session_manager.handle_request(scope, receive, send)
            return
```

### 5.5 启动服务器

```python
if workers > 1:
    # 多进程模式
    uvicorn.run(
        "doris_mcp_server.multiworker_app:app",
        host=host,
        port=port,
        workers=workers,
        log_level="info"
    )
else:
    # 单进程模式
    config = uvicorn.Config(
        app=mcp_app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    # 启动会话管理器和服务器
    async with session_manager.run():
        await server.serve()
```

## 6. 安全认证流程

HTTP 模式下的 MCP 请求认证流程：

1. 从请求头或查询参数提取令牌：`await self._extract_auth_info_from_scope(scope, headers)`
2. 认证请求：`auth_context = await self.security_manager.authenticate_request(auth_info)`
3. 存储认证上下文：`scope["auth_context"] = auth_context`
4. 设置上下文变量：`auth_context_var.set(auth_context)`（供工具访问）

## 7. 服务器关闭流程 (`shutdown()`)

```python
async def shutdown(self):
    # 关闭安全管理器（包括 JWT 清理）
    await self.security_manager.shutdown()
    
    # 关闭数据库连接
    await self.connection_manager.close()
```

## 8. 调用顺序总结

### 8.1 初始化阶段
```
main_sync() → main() → DorisServer.__init__() → _setup_handlers()
```

### 8.2 STDIO 模式启动
```
main() → server.start_stdio() → security_manager.initialize() → 
connection_manager.initialize_for_stdio_mode() → stdio_server() → server.run()
```

### 8.3 HTTP 模式启动
```
main() → server.start_http() → security_manager.initialize() → 
connection_manager.initialize_for_http_mode() → StreamableHTTPSessionManager() → 
create ASGI app → uvicorn.run()
```

### 8.4 请求处理流程
```
HTTP 请求 → mcp_app() → _extract_auth_info_from_scope() → 
security_manager.authenticate_request() → session_manager.handle_request() → 
相应的 MCP 处理器（handle_list_tools, handle_call_tool 等）
```

## 9. 核心组件交互图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Doris MCP Server                               │
├─────────┬─────────┬───────────┬───────────┬───────────┬─────────────────┤
│  MCP    │ Security│ Connection│ Resources │  Tools    │   Prompts       │
│ Server  │ Manager │  Manager  │  Manager  │  Manager  │   Manager       │
└────┬────┴────┬────┴────┬──────┴────┬──────┴────┬──────┴────────┬───────┘
     │         │         │           │           │               │
     ▼         ▼         ▼           ▼           ▼               ▼
┌─────────┐ ┌─────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────────┐
│ MCP     │ │ JWT/    │ │ Database  │ │ Resource  │ │ Tool            │
│ Protocol│ │ OAuth2  │ │ Connection│ │ Providers │ │ Implementations│
└─────────┘ └─────────┘ └───────────┘ └───────────┘ └─────────────────┘
```

## 10. 关键依赖关系

- **MCP 框架**：提供核心协议支持
- **Starlette**：用于 HTTP 模式的 ASGI 框架
- **Uvicorn**：ASGI 服务器
- **Doris 数据库**：通过连接管理器访问
- **JWT/OAuth2**：用于安全认证

## 11. 配置与环境变量

主要配置项：
- `TRANSPORT`：传输模式（stdio/http）
- `SERVER_HOST`：HTTP 服务器主机地址
- `SERVER_PORT`：HTTP 服务器端口
- `DORIS_HOST`：Doris 数据库主机
- `DORIS_PORT`：Doris 数据库端口
- `DORIS_USER`：Doris 数据库用户名
- `DORIS_PASSWORD`：Doris 数据库密码
- `DORIS_DATABASE`：Doris 数据库名
- `LOG_LEVEL`：日志级别

## 12. 命令行参数示例

```bash
# STDIO 模式启动
python -m doris_mcp_server --transport stdio --doris-host localhost --doris-port 9030

# HTTP 模式启动
python -m doris_mcp_server --transport http --host 0.0.0.0 --port 3000 --workers 4
```

## 13. 注意事项

1. **版本兼容性**：代码包含 MCP 1.8.x 和 1.9.x 的兼容处理
2. **安全认证**：HTTP 模式下的 MCP 请求需要认证
3. **资源管理**：服务器会自动处理资源清理
4. **多进程模式**：HTTP 模式支持多进程部署，提高并发能力
5. **错误处理**：包含详细的错误日志和异常处理机制