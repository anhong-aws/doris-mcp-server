# Doris MCP Server 多进程架构与分布式部署分析

## 1. 当前架构概述

### 1.1 单服务器多进程模式

Doris MCP Server 的多进程模式基于 uvicorn 实现，核心特点：

- **主进程**：负责绑定 socket、启动 Worker 进程
- **Worker 进程**：每个 Worker 独立初始化、独立处理请求
- **进程隔离**：每个 Worker 有独立的数据库连接和安全管理器
- **负载均衡**：由操作系统内核通过 accept 队列自动完成

```
┌─────────────────────────────────────────────────────────────┐
│                    服务器 (单台)                             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  uvicorn 主进程                                      │    │
│  │    - 绑定 0.0.0.0:3000 端口                         │    │
│  │    - fork() 4 个 Worker 进程                        │    │
│  │    - 监听子进程状态                                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│         ┌─────────────────────────────────────────┐          │
│         │     Linux 内核 accept 队列              │          │
│         │     (round-robin 分发)                  │          │
│         └─────────────────────────────────────────┘          │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐               │
│         │                 │                 │               │
│         ▼                 ▼                 ▼               │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐           │
│   │ Worker 1 │     │ Worker 2 │     │ Worker 3 │           │
│   │ PID 100  │     │ PID 101  │     │ PID 102  │           │
│   └────┬─────┘     └────┬─────┘     └────┬─────┘           │
│        │                │                │                  │
│        └────────────────┴────────────────┘                  │
│                         │                                   │
│                         ▼                                   │
│              每个 Worker 独立处理请求                        │
│              • 验证 Token                                   │
│              • 执行 Tool/Resource/Prompt                    │
│              • 返回响应                                     │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 核心代码流程

#### 主进程启动（main.py）

```python
# doris_mcp_server/main.py
if workers > 1:
    # 多进程模式
    uvicorn.run(
        "doris_mcp_server.multiworker_app:app",
        host=host,
        port=port,
        workers=workers,      # Worker 数量
        log_level="info"
    )
```

#### Worker 独立初始化（multiworker_app.py）

```python
# doris_mcp_server/multiworker_app.py

# 全局变量（每个进程独立）
_worker_server = None
_worker_session_manager = None
_worker_connection_manager = None
_worker_security_manager = None
_worker_initialized = False

async def initialize_worker():
    """每个 Worker 进程独立初始化"""
    global _worker_server, _worker_connection_manager, _worker_initialized
    
    if _worker_initialized:
        return  # 防止重复初始化
    
    # 1. 独立创建配置
    config = DorisConfig.from_env()
    
    # 2. 独立创建安全管理器
    _worker_security_manager = DorisSecurityManager(config)
    await _worker_security_manager.initialize()
    
    # 3. 独立创建数据库连接管理器
    _worker_connection_manager = DorisConnectionManager(config, ...)
    await _worker_connection_manager.initialize()
    
    # 4. 独立创建 MCP 服务器
    _worker_server = Server("doris-mcp-server")
    
    # 5. 独立创建会话管理器
    _worker_session_manager = StreamableHTTPSessionManager(
        app=_worker_server,
        stateless=True
    )
    
    _worker_initialized = True
```

#### 请求处理（multiworker_app.py）

```python
async def mcp_asgi_app(scope, receive, send):
    """当前 Worker 直接处理请求"""
    if not _worker_initialized:
        await send({'type': 'http.response.start', 'status': 503, ...})
        return
    
    # 当前 Worker 处理请求
    await _worker_session_manager.handle_request(scope, receive, send)
```

### 1.3 进程生命周期管理

```python
@asynccontextmanager
async def lifespan(app):
    """应用生命周期管理"""
    # Startup
    await initialize_worker()
    yield
    
    # Shutdown - 清理当前 Worker 资源
    if _worker_session_manager_context:
        await _worker_session_manager_context.__aexit__(None, None, None)
    if _worker_connection_manager:
        await _worker_connection_manager.close()
    if _worker_security_manager:
        await _worker_security_manager.shutdown()
```

## 2. 启动命令与配置

### 2.1 命令行启动

```bash
# 单 Worker（默认）
python -m doris_mcp_server --transport http

# 多 Worker（生产环境推荐）
python -m doris_mcp_server --transport http --workers 4

# 自动检测 CPU 核心数
python -m doris_mcp_server --transport http --workers 0

# 指定端口
python -m doris_mcp_server --transport http --port 8080 --workers 4
```

### 2.2 环境变量配置

```bash
export WORKERS=4                    # Worker 数量
export SERVER_HOST=0.0.0.0          # 监听地址
export SERVER_PORT=3000             # 端口
export DORIS_HOST=localhost         # Doris 数据库地址
export DORIS_PORT=9030              # Doris 端口
export DORIS_USER=root              # 用户名
export DORIS_PASSWORD=password      # 密码
export DORIS_DATABASE=db_name       # 数据库名
export LOG_LEVEL=INFO               # 日志级别
```

### 2.3 启动流程

```
1. python -m doris_mcp_server --transport http --workers 4
           │
           ▼
2. main() → DorisServer(config)
           │
           ▼
3. uvicorn.run(..., workers=4)
           │
           ▼
4. uvicorn 主进程：
   - 创建 socket，bind(0.0.0.0:3000)
   - fork() 4 个 Worker 进程
   - 每个 Worker 继承 socket 描述符
           │
           ▼
5. 每个 Worker 进程：
   - 执行 initialize_worker()
   - 独立创建 MCP 服务器
   - 独立创建数据库连接
   - 开始监听 socket
           │
           ▼
6. 客户端请求到达：
   - Linux 内核 accept() 队列
   - round-robin 分发给空闲 Worker
   - Worker 处理请求并返回
```

## 3. 当前架构的局限性

### 3.1 无法跨服务器部署

| 特性 | 当前实现 | 限制 |
|------|---------|------|
| **进程管理** | fork() 子进程 | 只能在单机上创建子进程 |
| **状态共享** | 进程内全局变量 | 进程间无法共享 |
| **负载均衡** | OS 内核 accept 队列 | 只能在本机内部分发 |
| **水平扩展** | 增加单机 Worker 数 | 受单机资源限制 |

### 3.2 单点故障风险

- **主进程崩溃**：所有 Worker 一起崩溃
- **单机故障**：整个服务不可用
- **资源限制**：单机 CPU/内存/网络有限

### 3.3 状态隔离问题

当前实现依赖进程隔离：

```python
# 每个 Worker 独立的全局变量
_worker_security_manager  # Token/JWT 状态（进程内）
_token_handlers           # Token 管理器（进程内）
```

**问题**：如果需要：
- Token 撤销：需要通知所有 Worker 刷新
- JWT 验证：每个 Worker 独立验证
- 会话管理：无法跨 Worker 共享

## 4. 分布式部署架构

### 4.1 目标架构

```
                          ┌─────────────────────────────────────────┐
                          │      负载均衡层                          │
                          │   Nginx / HAProxy / 云 LB               │
                          │   监听 80/443 端口                       │
                          │   • 健康检查                             │
                          │   • SSL 终止                             │
                          │   • 流量分发                             │
                          └────────────────┬────────────────────────┘
                                           │
                      ┌────────────────────┼────────────────────┐
                      │                    │                    │
                      ▼                    ▼                    ▼
          ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
          │    Server 1       │ │    Server 2       │ │    Server 3       │
          │  ┌─────────────┐  │ │  ┌─────────────┐  │ │  ┌─────────────┐  │
          │  │ uvicorn     │  │ │  │ uvicorn     │  │ │  │ uvicorn     │  │
          │  │ workers=4   │  │ │  │ workers=4   │  │ │  │ workers=4   │  │
          │  └─────────────┘  │ │  └─────────────┘  │ │  └─────────────┘  │
          └───────────────────┘ └───────────────────┘ └───────────────────┘
                      │                    │                    │
                      └────────────────────┼────────────────────┘
                                           │
                                           ▼
                          ┌─────────────────────────────────────────┐
                          │         共享存储层                       │
                          │   • Redis (Token/JWT/会话)               │
                          │   • 统一配置管理                         │
                          └─────────────────────────────────────────┘
                                           │
                                           ▼
                          ┌─────────────────────────────────────────┐
                          │       Apache Doris 数据库                │
                          └─────────────────────────────────────────┘
```

### 4.2 分布式改造需要的改动

#### 4.2.1 状态存储改造

| 组件 | 当前实现 | 分布式实现 |
|------|---------|-----------|
| **Token 管理** | 进程内 `InMemoryTokenStore` | Redis Token Store |
| **JWT 验证** | 本地验证 | 共享密钥或 Redis 验证 |
| **会话管理** | 进程内 | Redis Session Store |
| **OAuth 状态** | 进程内 | Redis OAuth State |

**改造示例**：

```python
# 当前：进程内存储
class InMemoryTokenStore:
    def __init__(self):
        self._tokens = {}  # 进程内字典

# 分布式：Redis 存储
class RedisTokenStore:
    def __init__(self, redis_client):
        self._redis = redis_client  # Redis 连接
    
    async def validate_token(self, token_id: str) -> bool:
        # 从 Redis 获取并验证
        return await self._redis.exists(f"token:{token_id}")
    
    async def revoke_token(self, token_id: str):
        # 删除 Redis 中的 token
        await self._redis.delete(f"token:{token_id}")
```

#### 4.2.2 配置中心

```python
# 当前：环境变量
config = DorisConfig.from_env()

# 分布式：统一配置中心
config = await ConfigCenter.get_config("doris-mcp-server")
# 支持：
# - 动态更新配置
# - 多服务器配置同步
# - 配置版本管理
```

#### 4.2.3 部署脚本

```bash
# 部署脚本示例
#!/bin/bash

# Server 1
ssh server1 "cd /opt/doris-mcp-server && docker-compose up -d"

# Server 2
ssh server2 "cd /opt/doris-mcp-server && docker-compose up -d"

# Server 3
ssh server3 "cd /opt/doris-mcp-server && docker-compose up -d"

# 更新 Nginx 负载均衡配置
ansible-playbook update-nginx.yml
```

#### 4.2.4 Docker 部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  doris-mcp:
    build: .
    ports:
      - "3000:3000"
    environment:
      - REDIS_URL=redis://redis:6379
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=3000
      - WORKERS=4
    depends_on:
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

### 4.3 改造优先级

| 优先级 | 改造项 | 难度 | 影响 |
|--------|--------|------|------|
| **P0** | Redis Token Store | 中 | Token 跨服务器验证 |
| **P0** | 共享 JWT 密钥 | 低 | JWT 验证一致性 |
| **P1** | Redis Session Store | 中 | 会话跨服务器共享 |
| **P1** | 配置中心 | 高 | 动态配置更新 |
| **P2** | 健康检查接口 | 低 | 负载均衡健康检测 |
| **P2** | 指标监控 | 中 | 运维监控 |

### 4.4 风险与注意事项

1. **Redis 可用性**
   - Redis 成为单点故障风险
   - 需要 Redis 集群或哨兵模式

2. **网络延迟**
   - 额外的 Redis 网络开销
   - 需要考虑缓存策略

3. **数据一致性**
   - Token 撤销的最终一致性
   - 需要适当的重试和补偿机制

4. **安全**
   - Redis 连接加密
   - Token 存储加密

## 5. 总结

### 5.1 当前架构优点

- 部署简单，单机即可运行
- 进程隔离，故障影响范围小
- 无额外依赖（不需要 Redis）
- 适合中小规模部署

### 5.2 适用场景

| 场景 | 推荐配置 |
|------|---------|
| 开发/测试 | 单 Worker (默认) |
| 小规模生产 | 2-4 Workers，单机 |
| 中大规模 | 需要分布式改造 |
| 高可用 | 分布式部署 + 负载均衡 |

### 5.3 下一步建议

1. **短期**：优化单机多 Worker 配置
   - 根据 CPU 核心数调整 Worker 数量
   - 优化数据库连接池配置

2. **中期**：引入 Redis 支持
   - Token Store 改造
   - JWT 密钥共享

3. **长期**：完整分布式部署
   - 多服务器部署
   - 负载均衡配置
   - 监控告警体系

## 6. 参考配置

### 6.1 单机生产配置

```bash
# 环境变量
export WORKERS=4
export SERVER_HOST=0.0.0.0
export SERVER_PORT=3000
export DORIS_HOST=your-doris-host
export DORIS_PORT=9030
export DORIS_USER=your-user
export DORIS_PASSWORD=your-password
export DORIS_DATABASE=your-database
export LOG_LEVEL=INFO
export MAX_CONNECTIONS=100
export CONNECTION_POOL_SIZE=20
```

### 6.2 systemd 服务配置

```ini
# /etc/systemd/system/doris-mcp.service
[Unit]
Description=Apache Doris MCP Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/doris-mcp-server
Environment=WORKERS=4
Environment=SERVER_PORT=3000
ExecStart=/opt/doris-mcp-server/.venv/bin/python -m doris_mcp_server --transport http
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

### 6.3 Nginx 负载均衡配置

```nginx
upstream doris_mcp {
    least_conn;  # 最少连接数算法
    
    server 10.0.0.1:3000 weight=1 max_fails=3 fail_timeout=30s;
    server 10.0.0.2:3000 weight=1 max_fails=3 fail_timeout=30s;
    server 10.0.0.3:3000 weight=1 max_fails=3 fail_timeout=30s;
    
    keepalive 32;  # 保持连接
}

server {
    listen 80;
    server_name mcp.your-domain.com;
    
    location / {
        proxy_pass http://doris_mcp;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Connection "";
        
        # MCP 特殊处理
        proxy_buffering off;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://doris_mcp/health;
    }
}
```
