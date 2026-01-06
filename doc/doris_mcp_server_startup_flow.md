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

`initialize_for_http_mode()` 方法会根据环境变量配置决定连接池的初始化策略：

- **有全局配置时**：尝试验证全局数据库配置，如果有效则创建全局连接池供所有请求共享
- **无全局配置时**：系统优雅降级，转而使用 token-bound 数据库配置模式

在 token-bound 配置模式下，MCP 连接建立时会根据请求中的 token 从 `tokens.json` 中获取对应的数据库连接配置，并动态创建连接池。

**架构限制说明**：
由于当前架构中全局连接池只有一个实例，当配置了全局数据库连接时，该连接池会被所有客户端请求共享。如果需要连接不同的 Doris 数据库实例（即不同 token 对应不同数据库），目前存在以下限制：

1. **多数据库场景**：不支持同时连接多个不同的 Doris 数据库实例，全局连接池会被后续配置覆盖
2. **多 token 并发**：在全局配置模式下，不同 token 客户端无法使用不同的数据库连接
3. **解决方案**：
   - 方案一：不配置全局环境变量，改用纯 token-bound 模式（推荐）
   - 方案二：所有客户端连接同一个 Doris 数据库实例，通过不同的 token 实现权限隔离

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

## 14. 服务器关闭流程详解

### 14.1 关闭触发方式

服务器支持多种关闭触发方式：

| 触发方式 | 信号/操作 | 行为 |
|---------|----------|------|
| Ctrl+C | SIGINT | 触发优雅关闭 |
| `kill <pid>` | SIGTERM | 触发优雅关闭 |
| `kill -9 <pid>` | SIGKILL | 立即终止，不执行清理 |
| uvicorn 超时 | 内部计时器 | 超时后强制关闭 |

### 14.2 关闭流程详解

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         服务器关闭流程                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────┐                                                     │
│  │ 收到关闭信号   │                                                     │
│  └───────┬───────┘                                                     │
│          │                                                             │
│          ▼                                                             │
│  ┌───────────────────────────────────────────┐                         │
│  │ uvicorn 收到关闭信号                       │                         │
│  │ - 停止接受新连接                           │                         │
│  │ - 设置超时计时器 (timeout_graceful_shutdown)│                         │
│  └───────┬───────────────────────────────────┘                         │
│          │                                                             │
│          ▼                                                             │
│  ┌───────────────────────────────────────────┐                         │
│  │ Starlette lifespan 上下文管理器             │                         │
│  │ - 执行 finally 块                          │                         │
│  │ - 调用 server.shutdown()                   │                         │
│  └───────┬───────────────────────────────────┘                         │
│          │                                                             │
│          ▼                                                             │
│  ┌───────────────────────────────────────────┐                         │
│  │ 1. security_manager.shutdown()            │                         │
│  │    - JWT 令牌清理                          │                         │
│  │    - OAuth 状态清理                        │                         │
│  │    - Token 缓存清理                        │                         │
│  └───────┬───────────────────────────────────┘                         │
│          │                                                             │
│          ▼                                                             │
│  ┌───────────────────────────────────────────┐                         │
│  │ 2. connection_manager.close()             │                         │
│  │    - 关闭所有连接池                        │                         │
│  │    - 取消活跃的连接                        │                         │
│  │    - 停止后台健康检查任务                   │                         │
│  └───────┬───────────────────────────────────┘                         │
│          │                                                             │
│          ▼                                                             │
│  ┌───────────────────────────────────────────┐                         │
│  │ uvicorn 超时处理                           │                         │
│  │ - 如果 5秒 内未完成优雅关闭                 │                         │
│  │ - 取消所有 running tasks                   │                         │
│  │ - 强制关闭剩余连接                          │                         │
│  └───────┬───────────────────────────────────┘                         │
│          │                                                             │
│          ▼                                                             │
│  ┌───────────────────────────────────────────┐                         │
│  │ 进程退出                                   │                         │
│  └───────────────────────────────────────────┘                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 14.3 核心关闭代码

```python
# Starlette lifespan 上下文管理器
@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    """管理应用生命周期"""
    logger.info("Application started!")
    try:
        yield
    finally:
        logger.info("Application is shutting down...")
        # 确保即使超时也会执行 shutdown
        await self.shutdown()

# 服务器关闭方法
async def shutdown(self):
    """关闭服务器并清理资源"""
    self.logger.info("Shutting down Doris MCP Server")
    try:
        # 1. 关闭安全管理器（包括 JWT 清理）
        await self.security_manager.shutdown()
        self.logger.info("Security manager shutdown completed")
        
        # 2. 关闭连接管理器
        await self.connection_manager.close()
        self.logger.info("Connection manager shutdown completed")
        
        # 3. 关闭 uvicorn 服务器
        if self._uvicorn_server and self._uvicorn_server.started:
            self._uvicorn_server.stop()
        
        self.logger.info("Doris MCP Server has been shut down")
    except Exception as e:
        self.logger.error(f"Error occurred while shutting down server: {e}")
```

### 14.4 uvicorn 超时配置

```python
# 单进程模式下的 uvicorn 配置
config = uvicorn.Config(
    app=mcp_app,
    host=host,
    port=port,
    log_level="info",
    timeout_graceful_shutdown=5  # 5秒超时
)
server = uvicorn.Server(config)
```

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `timeout_graceful_shutdown` | 5 秒 | 收到关闭信号后等待优雅关闭的最长时间 |

### 14.5 超时后的行为

当 uvicorn 超时时：

```
ERROR: Cancel 1 running task(s), timeout graceful shutdown exceeded
INFO:  Waiting for application shutdown.
INFO:  Application shutdown complete.
INFO:  Finished server process
```

1. **取消 running tasks**：uvicorn 取消所有正在运行的异步任务
2. **等待 application shutdown**：等待 lifespan 的 finally 块执行
3. **完成清理**：即使某些任务被取消，shutdown() 方法仍会执行
4. **进程退出**：所有清理完成后进程退出

### 14.6 主函数中的关闭处理

```python
async def main():
    server = DorisServer(config)
    
    try:
        if config.transport == "http":
            await server.start_http(...)
        else:
            await server.start_stdio()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down server...")
    except Exception as e:
        logger.error(f"Server runtime error: {e}")
        return 1
    finally:
        # 正常关闭或异常时的清理
        await server.shutdown()
        shutdown_logging()
    return 0
```

### 14.7 不同信号的行为对比

| 信号 | 可捕获 | 执行 shutdown | 执行顺序 |
|------|--------|---------------|----------|
| SIGINT (Ctrl+C) | ✅ | ✅ | 优雅关闭 → 超时 → 强制 |
| SIGTERM (kill) | ✅ | ✅ | 优雅关闭 → 超时 → 强制 |
| SIGKILL (kill -9) | ❌ | ❌ | 立即终止 |

### 14.8 后台运行时的关闭方式

当服务以 `nohup python ... &` 方式启动时：

```bash
# 方式1: 使用 pkill（推荐）
pkill -f "doris_mcp_server"

# 方式2: 通过端口找到进程
lsof -ti:3000 | xargs kill  # 关闭端口 3000 的进程

# 方式3: 强制关闭
kill -9 $(lsof -ti:3000)
```

### 14.9 关闭时的注意事项

1. **lifespan 的 finally 块**：确保即使 uvicorn 超时也会执行清理
2. **异常处理**：shutdown 方法应捕获异常，避免影响其他清理操作
3. **超时配置**：合理设置 `timeout_graceful_shutdown`，避免过长等待
4. **信号处理**：`kill -9` 会直接终止进程，无法执行任何清理
5. **日志系统**：关闭后需要调用 `shutdown_logging()` 刷新日志