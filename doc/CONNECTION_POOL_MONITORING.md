# Doris MCP Server 连接池监控技术文档

## 一、概述

本文档详细描述了 Doris MCP Server 中连接池监控体系的设计与实现，涵盖连接池健康检查机制、无效连接识别策略以及连接销毁流程。该监控体系采用主动式检测与被动式清理相结合的方式，确保数据库连接的高可用性和性能稳定性。连接池作为数据库访问的核心组件，其健康状态直接影响整个服务的稳定性和响应能力。通过实现完善的监控机制，系统能够在连接异常发生之前及时发现潜在问题，并采取相应的恢复措施，从而避免因连接问题导致的业务中断。监控体系的设计遵循高可靠性、低侵入性和实时响应的原则，通过后台任务持续监控连接池状态，并在发现异常时自动执行恢复流程。

## 二、监控架构

### 2.1 核心数据结构

连接池监控体系的基础是 `ConnectionMetrics` 数据类，它定义了用于追踪连接池性能的关键指标。这些指标为监控和诊断提供了量化的依据，使运维人员能够准确了解连接池的运行状态。数据类采用 Python 的 `@dataclass` 装饰器实现，自动生成初始化方法和属性访问器，简化了代码结构的同时保证了类型安全性。

```python
@dataclass
class ConnectionMetrics:
    """Connection pool performance metrics"""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    connection_errors: int = 0
    avg_connection_time: float = 0.0
    last_health_check: datetime | None = None
```

各指标的具体含义如下所述。`total_connections` 表示连接池中已创建的总连接数，包括活跃连接和空闲连接，该指标用于评估连接池的使用规模和增长趋势。`active_connections` 表示当前正在被应用程序使用的连接数量，反映了并发的数据库操作强度。`idle_connections` 表示当前处于空闲状态、可以被重新分配的连接数量，该指标对于评估连接池的容量规划至关重要。`failed_connections` 表示连接创建或使用过程中失败的连接总数，该计数器可用于监控系统稳定性。`connection_errors` 记录了连接过程中发生的错误总次数，通过分析该指标可以识别潜在的系统问题。`avg_connection_time` 计算了建立数据库连接所需的平均时间，是评估数据库性能的重要参考。`last_health_check` 记录了上次健康检查的时间戳，用于判断监控系统的运行状态和检查频率。

### 2.2 DorisConnectionManager 监控组件

`DorisConnectionManager` 是连接池监控的核心管理类，集成了连接池创建、健康检查、故障恢复和指标收集等功能。该类采用异步编程模式，充分利用 Python 的 `asyncio` 框架实现高效的并发连接管理。在初始化阶段，类会设置一系列监控相关的参数和状态变量，为后续的监控任务奠定基础。

```python
class DorisConnectionManager:
    def __init__(self, config, security_manager=None, token_manager=None):
        # 连接池实例
        self.pool: Pool | None = None
        
        # 连接池状态管理
        self.pool_recovering = False
        self.pool_health_check_task = None
        self.pool_cleanup_task = None
        
        # 指标追踪
        self.metrics = ConnectionMetrics()
        
        # 并发控制锁
        self._connection_lock = asyncio.Lock()
        self._recovery_lock = asyncio.Lock()
        self._connection_semaphore = asyncio.Semaphore(value=20)
        
        # 监控参数配置
        self.health_check_interval = 30  #  seconds
        self.pool_recycle = config.database.max_connection_age or 3600  # 1 hour
        self.minsize = config.database.min_connections  # 默认为0
        self.maxsize = config.database.max_connections or 20
```

状态管理变量 `pool_recovering` 用于标识连接池是否正在进行恢复操作，防止在恢复过程中触发重复的恢复流程，确保系统稳定运行。后台任务引用 `pool_health_check_task` 和 `pool_cleanup_task` 分别指向健康监控和连接清理的异步任务，通过这些任务系统能够持续监控连接池状态。指标对象 `metrics` 存储了连接池的运行数据，为诊断和报告提供支持。

并发控制机制对于多线程环境下的连接池管理至关重要。`_connection_lock` 用于保护连接获取操作的原子性，防止竞态条件的发生。`_recovery_lock` 确保恢复操作的独占执行，避免多个恢复流程同时运行造成的资源浪费。`_connection_semaphore` 限制了并发连接获取的最大数量，防止系统在高负载下过度消耗数据库资源。

### 2.2.1 Python asyncio.Task 机制详解

理解后台监控任务能够持续运行的关键在于掌握 Python `asyncio` 的 Task 机制。`asyncio.Task` 是 Python 异步编程的核心概念，它将协程包装为可独立调度的执行单元，由事件循环统一管理。与传统的多线程不同，协程是协作式多任务，由开发者显式让出执行权，而非操作系统抢占式调度。事件循环（Event Loop）是 asyncio 应用的心脏，它负责调度协程的执行顺序、管理 I/O 操作的完成通知，以及处理定时器回调。当我们使用 `asyncio.create_task()` 创建任务时，实际上是将协程函数提交给事件循环进行调度执行。

```python
# 任务创建示例
self.pool_health_check_task = asyncio.create_task(self._pool_health_monitor())
self.pool_cleanup_task = asyncio.create_task(self._pool_cleanup_monitor())
```

这两行代码创建了两个持续运行的后台任务，它们在后台默默执行监控逻辑，而主程序可以继续处理其他请求。任务的持续运行依赖于其内部的无限循环设计和事件循环的持续运行。`_pool_health_monitor()` 方法包含一个 `while True` 循环，在每次迭代中执行健康检查操作，然后调用 `await asyncio.sleep(interval)` 让出控制权。这个 sleep 操作是实现周期性执行的关键：当协程执行到 await 表达式时，它会暂停执行并释放 CPU 资源，允许事件循环去执行其他就绪的协程。当 sleep 完成后，事件循环会将控制权交还给该协程，使其继续执行下一次循环。这种"执行-等待-执行-等待"的模式使得单个线程能够同时处理大量并发任务，同时保持资源的高效利用。

```python
async def _pool_health_monitor(self):
    """Background task to monitor pool health"""
    self.logger.info("🩺 Starting pool health monitor")
    
    while True:
        try:
            await asyncio.sleep(self.health_check_interval)  # 等待期间让出控制权
            await self._check_pool_health()                  # 等待结束后执行检查
        except asyncio.CancelledError:
            self.logger.info("Pool health monitor stopped")
            break
        except Exception as e:
            self.logger.error(f"Pool health monitor error: {e}")
```

任务的生命周期管理同样重要。任务创建后会返回一个 Task 对象，我们可以持有这个引用以便后续管理。当程序正常关闭时，我们需要取消这些后台任务以释放资源。取消操作通过调用 `task.cancel()` 实现，这会触发协程内部的 `asyncio.CancelledError` 异常。协程代码需要正确处理这个异常，通常是在 catch 块中执行必要的清理工作并正常退出循环。这就是为什么在代码中我们看到 `except asyncio.CancelledError: break` 的设计——它确保任务能够优雅地停止，而不是被强制终止导致资源泄漏。

事件循环的持续运行是任务能够一直运行的前提条件。在一个典型的 asyncio 应用中，事件循环会一直运行直到所有任务完成或被取消。由于我们的监控任务设计为无限循环，它们会一直存在于事件循环的任务列表中，事件循环也会持续调度它们执行。这种设计模式非常适合需要长期运行的后台服务，如监控、定时任务、心跳检测等场景。通过将监控逻辑封装在协程中并创建为后台任务，我们实现了高效且资源友好的持续监控机制。

### 2.3 ConnectionPoolMonitor 监控器

`ConnectionPoolMonitor` 类提供了高层次的监控接口和报告生成功能，是连接池监控体系对外暴露的主要接口。该类封装了复杂的监控逻辑，以简洁的 API 形式提供给外部调用，简化了监控数据的获取流程。

```python
class ConnectionPoolMonitor:
    """Connection pool monitor
    
    Provides detailed monitoring and reporting capabilities 
    for connection pool status
    """

    def __init__(self, connection_manager: DorisConnectionManager):
        self.connection_manager = connection_manager
        self.logger = get_logger(__name__)
```

监控器的设计遵循了关注点分离的原则，`DorisConnectionManager` 负责底层的连接管理和状态维护，而 `ConnectionPoolMonitor` 则专注于数据的聚合、格式化和报告生成。这种分层设计使得监控系统具有良好的可扩展性和可维护性，能够适应不同的监控需求和集成场景。

## 三、连接池健康检查

### 3.1 健康检查机制概述

连接池健康检查是监控体系的核心功能之一，通过定期执行数据库查询来验证连接的有效性和可用性。系统采用双层检查机制：单连接健康检查和连接池整体健康检查。单连接检查用于验证单个连接的状态，而连接池检查则评估整个连接池的运行状况。健康检查的设计充分考虑了效率和安全性的平衡，既要能够及时发现问题，又不能对正常业务造成显著的性能影响。

健康检查的执行遵循最小权限原则，检查操作仅使用 `SELECT 1` 这样的轻量级查询，不会对数据库造成额外的负担。同时，所有检查操作都设置了超时机制，确保检查过程本身不会因为网络或数据库问题而无限期阻塞。通过这种设计，健康检查能够在不影响业务正常运行的前提下，持续监控连接池的健康状态。

### 3.2 单连接健康检查

单连接健康检查通过 `DorisConnection` 类的 `ping()` 方法实现，该方法使用 `SELECT 1` 查询验证连接的有效性。检查过程包含多个验证步骤，确保能够准确识别各种类型的连接异常。方法采用了增强的错误检测机制，特别针对常见的 `at_eof` 错误进行了优化处理。

```python
async def ping(self) -> bool:
    """Check connection health status with enhanced at_eof error detection"""
    try:
        # 步骤1：检查连接对象是否存在且未关闭
        if not self.connection or self.connection.closed:
            self.is_healthy = False
            return False
        
        # 步骤2：使用安全的查询操作验证连接状态
        try:
            async with asyncio.timeout(3):  # 3 second timeout
                async with self.connection.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
                    if result and result[0] == 1:
                        self.is_healthy = True
                        return True
                    else:
                        self.logger.debug(f"Connection {self.session_id} ping query returned unexpected result")
                        self.is_healthy = False
                        return False
        
        except asyncio.TimeoutError:
            self.logger.debug(f"Connection {self.session_id} ping timed out")
            self.is_healthy = False
            return False
        except Exception as query_error:
            error_str = str(query_error).lower()
            if 'at_eof' in error_str or 'nonetype' in error_str:
                self.logger.debug(f"Connection {self.session_id} ping failed with at_eof error: {query_error}")
            else:
                self.logger.debug(f"Connection {self.session_id} ping failed: {query_error}")
            self.is_healthy = False
            return False
        
    except Exception as e:
        self.logger.debug(f"Connection {self.session_id} ping failed with unexpected error: {e}")
        self.is_healthy = False
        return False
```

检查流程的详细说明如下。第一步验证连接对象的基本有效性，确保连接对象存在且未被手动关闭，这一步能够快速排除已经明确失效的连接，避免后续不必要的查询操作。第二步执行实际的健康探测，使用 `SELECT 1` 查询验证数据库连接的功能完整性，该查询是 MySQL 协议中最轻量级的查询，不会产生额外的计算开销。查询执行时设置了 3 秒的超时时间，这是经过实践验证的合理值，既能覆盖正常的网络延迟，又能在连接明显异常时快速失败。第三步处理检查过程中可能出现的各种异常情况，包括超时错误和查询执行错误。对于特定的 `at_eof` 错误，系统能够识别并记录，这是异步 MySQL 连接中常见的连接断开指示。

### 3.3 连接池整体健康检查

连接池整体健康检查通过 `_test_pool_health()` 方法实现，该方法从连接池中获取一个连接并执行验证查询。与单连接检查不同，池级检查关注的是整个连接池的可用性，而不仅仅是单个连接的状态。

```python
async def _test_pool_health(self) -> bool:
    """Test connection pool health"""
    try:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")
                result = await cursor.fetchone()
                return result and result[0] == 1
    except Exception as e:
        self.logger.error(f"Pool health test failed: {e}")
        return False
```

池级健康检查的实现相对简洁，但蕴含着重要的设计考量。通过从池中获取连接并执行查询，检查不仅验证了数据库服务器的可访问性，还验证了连接池本身的工作状态。如果获取连接或执行查询失败，系统能够及时发现并触发相应的恢复流程。这种设计确保了健康检查能够发现各类潜在问题，包括网络故障、数据库服务器异常和连接池配置问题等。

### 3.4 后台健康监控任务

健康监控采用后台异步任务的方式持续运行，通过 `_pool_health_monitor()` 方法实现。该任务按照设定的时间间隔周期性地执行健康检查，并将检查结果记录到指标系统中。任务设计遵循了优雅停止的原则，能够正确处理取消信号和异常情况。

```python
async def _pool_health_monitor(self):
    """Background task to monitor pool health"""
    self.logger.info("🩺 Starting pool health monitor")
    
    while True:
        try:
            await asyncio.sleep(self.health_check_interval)
            await self._check_pool_health()
        except asyncio.CancelledError:
            self.logger.info("Pool health monitor stopped")
            break
        except Exception as e:
            self.logger.error(f"Pool health monitor error: {e}")
```

健康监控任务的核心逻辑是一个无限循环，在每次迭代中首先等待设定的时间间隔，然后执行健康检查操作。默认的检查间隔为 30 秒，这是一个在监控及时性和系统开销之间取得平衡的值。间隔过短会增加数据库的负载和对网络带宽的占用，间隔过长则可能延迟对故障的发现。任务能够正确响应 `asyncio.CancelledError` 异常，这是 Python 异步任务取消时抛出的标准异常，确保任务能够被正确终止而不留下资源泄漏。

### 3.5 健康状态检查与恢复

`_check_pool_health()` 方法是健康检查的核心逻辑所在，它协调了健康验证和故障恢复两个关键环节。该方法首先检查是否有其他恢复操作正在进行中，避免并发恢复导致的资源竞争问题，然后执行实际的健康验证，最后根据验证结果决定是否需要启动恢复流程。

```python
async def _check_pool_health(self):
    """Check and maintain pool health"""
    try:
        # 跳过正在恢复的连接池检查
        if self.pool_recovering:
            self.logger.debug("Pool recovery in progress, skipping health check")
            return
            
        # 执行健康测试
        health_ok = await self._test_pool_health()
        
        if health_ok:
            self.logger.debug("✅ Pool health check passed")
            self.metrics.last_health_check = datetime.utcnow()
        else:
            self.logger.warning("❌ Pool health check failed, attempting recovery")
            await self._recover_pool()
            
    except Exception as e:
        self.logger.error(f"Pool health check error: {e}")
        await self._recover_pool()
```

健康检查的实现体现了防御性编程的思想。当检测到健康状态正常时，系统会更新指标记录检查时间，以便后续分析和审计。当检测到健康状态异常时，系统会立即启动恢复流程，尝试重建连接池。同时，方法还包含了异常处理逻辑，确保任何意外错误都会触发恢复流程，而不是被静默忽略。

## 四、无效连接识别

### 4.1 无效连接的类型与特征

在数据库连接管理中，无效连接可能由多种原因导致，识别这些无效连接是维护连接池健康的关键环节。系统需要处理的无效连接主要包括以下几类。第一类是网络中断导致的连接失效，当网络出现瞬断或不稳定时，已建立的连接可能突然变得不可用。第二类是数据库服务器重启或故障恢复后，所有之前的连接都会失效，需要重新建立。第三类是连接超时引起的失效，长时间空闲的连接可能被数据库服务器关闭。第四类是协议错误导致的连接损坏，如 `at_eof` 错误表示连接的另一端已经关闭。第五类是资源限制导致的连接失效，如数据库服务器的连接数达到上限或用户权限被撤销。

识别无效连接的方法需要综合运用主动探测和被动检测两种策略。主动探测通过定期执行查询来验证连接的有效性，这种方法能够及时发现潜在问题，但会增加一定的系统开销。被动检测则在实际使用连接时观察操作是否成功，这种方法更加高效，但可能在连接失效到被发现之间存在延迟。系统结合使用两种方法，既保证了连接的可靠性，又控制了性能开销。

### 4.2 空闲连接检测

空闲连接检测通过 `_cleanup_stale_connections()` 方法实现，该方法定期检查连接池中的空闲连接，识别和清理可能已经失效的连接。检测策略采用抽样检查的方式，对部分空闲连接执行探测查询，根据探测结果决定是否需要销毁连接。

```python
async def _cleanup_stale_connections(self):
    """Proactively clean up potentially stale connections"""
    try:
        self.logger.debug("🧹 Checking for stale connections")
        
        # 获取连接池统计数据
        pool_size = self.pool.size
        pool_free = self.pool.freesize
        
        # 如果存在空闲连接，抽样测试其中的一部分
        if pool_free > 0:
            test_count = min(pool_free, 2)  # 最多测试2个空闲连接
            
            for i in range(test_count):
                try:
                    # 获取连接并测试其可用性
                    conn = await asyncio.wait_for(self.pool.acquire(), timeout=5)
                    
                    # 执行快速测试查询
                    async with conn.cursor() as cursor:
                        await asyncio.wait_for(cursor.execute("SELECT 1"), timeout=3)
                        await cursor.fetchone()
                    
                    # 连接正常，释放回连接池
                    self.pool.release(conn)
                    
                except asyncio.TimeoutError:
                    self.logger.debug(f"Stale connection test {i+1} timed out")
                    try:
                        await conn.ensure_closed()
                    except Exception:
                        pass
                except Exception as e:
                    self.logger.debug(f"Stale connection test {i+1} failed: {e}")
                    try:
                        await conn.ensure_closed()
                    except Exception:
                        pass
            
            self.logger.debug(f"Stale connection cleanup completed, tested {test_count} connections")
            
    except Exception as e:
        self.logger.error(f"Stale connection cleanup error: {e}")
```

空闲连接检测的实现采用了保守而高效的策略。系统不会检查所有空闲连接，而是选择最多两个连接进行抽样测试，这种设计在保证检测覆盖率的同时，避免了对性能的影响。检测过程设置了多个超时阈值：连接获取超时为 5 秒，查询执行超时为 3 秒，这些值确保了检测操作本身不会长时间占用系统资源。当检测到连接异常时，系统会立即关闭该连接，避免无效连接继续占用资源。

### 4.3 连接获取时的有效性验证

除了定期的空闲连接检测外，系统还在每次从连接池获取连接时进行有效性验证。这种双重检查机制确保了即使在两次定期检测之间失效的连接，也能够在使用时被及时发现和替换。

```python
async def get_connection(self, session_id: str) -> DorisConnection:
    """Acquire connection from pool with validation"""
    async with self._connection_semaphore:
        # 检查连接池是否可用
        if not self.pool:
            self.logger.warning("Connection pool is not available, attempting recovery...")
            await self._recover_pool_with_lock()
            if not self.pool:
                raise RuntimeError("Connection pool is not available and recovery failed")
        
        # 检查连接池是否已关闭
        if self.pool.closed:
            self.logger.warning("Connection pool is closed, attempting recovery...")
            await self._recover_pool_with_lock()
            if not self.pool or self.pool.closed:
                raise RuntimeError("Connection pool is closed and recovery failed")
        
        # 获取连接并验证其状态
        try:
            raw_conn = await asyncio.wait_for(self.pool.acquire(), timeout=10.0)
        except asyncio.TimeoutError:
            self.logger.error(f"Connection acquisition timed out for session {session_id}")
            await self._recover_pool_with_lock()
            raise RuntimeError("Connection acquisition timed out")
        
        # 基础验证：检查连接是否已关闭
        if raw_conn.closed:
            try:
                self.pool.release(raw_conn)
            except Exception:
                pass
            raise RuntimeError("Acquired connection is already closed")
        
        return DorisConnection(raw_conn, session_id, self.security_manager)
```

获取连接时的验证是连接生命周期管理中的重要环节。验证过程首先检查连接池本身的状态，确保池对象存在且未被关闭。然后尝试从池中获取一个连接，并设置合理的超时时间防止获取操作无限期阻塞。最后对获取到的连接进行基本的状态检查，确保连接对象是有效的。如果任何验证步骤失败，系统会触发相应的恢复或错误处理流程。

### 4.4 错误模式识别

系统能够识别多种连接错误模式，并根据不同的错误类型采取相应的处理策略。错误模式识别主要通过分析异常消息和错误代码来实现，其中特别关注了几类常见的连接错误。

`at_eof` 错误是异步 MySQL 连接中常见的错误类型，表示连接的读取端遇到了文件结束条件，通常意味着连接的另一端已经关闭。这类错误需要立即销毁连接并尝试重新获取有效连接。`nonetype` 错误通常表示连接对象已经变为 None，可能是由于资源耗尽或不当的资源清理导致的。超时错误表明连接响应异常，可能是因为网络问题或数据库服务器负载过高。连接拒绝错误可能表示数据库服务器出现了配置问题或权限变更。

通过识别这些错误模式，系统能够更精确地诊断连接问题的原因，并采取针对性的处理措施。这种智能的错误处理机制提高了系统的自愈能力，减少了人工干预的需要。

## 五、连接销毁流程

### 5.1 连接销毁的触发条件

连接销毁是连接池维护的重要操作，系统在多种情况下会触发连接的销毁流程。理解这些触发条件有助于更好地理解连接池的生命周期管理和资源优化策略。

定期清理触发是最常见的销毁触发条件。系统通过 `_pool_cleanup_monitor()` 后台任务定期执行空闲连接检测，当检测到无效连接时会立即将其销毁。这种主动式的清理策略能够及时移除过期或损坏的连接，保持连接池的健康状态。清理任务的执行频率为健康检查间隔的两倍，即默认 60 秒执行一次，这个频率在及时清理和资源消耗之间取得了平衡。

健康检查失败也会触发连接销毁。当 `_check_pool_health()` 方法检测到连接池整体健康状态异常时，会启动恢复流程，该流程涉及关闭整个现有连接池并重新创建新的连接池。这种机制确保了即使在发生严重故障时，系统也能够自动恢复到正常状态。

连接获取验证失败同样是重要的触发条件。当从连接池获取连接并进行基本验证时发现连接已关闭或处于异常状态，系统会拒绝使用该连接并尝试获取其他连接。如果连续获取失败，可能会触发连接池的重建操作。

此外，应用程序正常关闭时会触发所有连接的销毁流程，确保资源被正确释放。连接的生命周期达到预设的回收时间 `pool_recycle` 时，连接会被自动关闭并从池中移除，为新连接腾出空间。这种定期回收机制能够防止连接因长时间使用而可能出现的问题。

### 5.2 单连接销毁

单连接的销毁通过 `DorisConnection` 类的 `close()` 方法实现，该方法负责关闭底层数据库连接并释放相关资源。销毁过程需要处理各种可能的异常情况，确保操作本身不会引发新的问题。

```python
async def close(self):
    """Close connection"""
    try:
        if self.connection and not self.connection.closed:
            await self.connection.ensure_closed()
    except Exception as e:
        logging.error(f"Error occurred while closing connection: {e}")
```

单连接销毁的实现简洁但包含了必要的安全检查。首先验证连接对象存在且未被关闭，然后调用 `ensure_closed()` 方法执行实际的关闭操作。`ensure_closed()` 是 aiomysql 库提供的安全关闭方法，能够正确处理各种连接状态。最后，方法捕获并记录可能发生的任何异常，确保关闭操作的异常不会被传播到调用方。

### 5.3 连接池恢复与重建

当健康检查发现连接池整体状态异常时，系统会触发连接池的恢复流程，该流程通过 `_recover_pool()` 方法实现。恢复操作的核心是关闭现有连接池并创建新的连接池，同时确保恢复过程的原子性和幂等性。

```python
async def _recover_pool(self):
    """Recover connection pool when health check fails"""
    # 使用锁防止并发恢复
    async with self.pool_recovery_lock:
        if self.pool_recovering:
            self.logger.debug("Pool recovery already in progress, waiting...")
            return
            
        try:
            self.pool_recovering = True
            max_retries = 3
            retry_delay = 5  # seconds
            
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"🔄 Attempting pool recovery (attempt {attempt + 1}/{max_retries})")
                    
                    # 关闭现有连接池
                    if self.pool:
                        try:
                            if not self.pool.closed:
                                self.pool.close()
                                await asyncio.wait_for(self.pool.wait_closed(), timeout=3.0)
                            self.logger.debug("Old pool closed successfully")
                        except asyncio.TimeoutError:
                            self.logger.warning("Pool close timeout, forcing cleanup")
                        except Exception as e:
                            self.logger.warning(f"Error closing old pool: {e}")
                        finally:
                            self.pool = None
                    
                    # 重建连接池
                    if attempt > 0:
                        await asyncio.sleep(2)
                    
                    self.logger.debug("Creating new connection pool...")
                    self.pool = await asyncio.wait_for(
                        aiomysql.create_pool(
                            host=self.host,
                            port=self.port,
                            user=self.user,
                            password=self.password,
                            db=self.database,
                            charset=self.charset,
                            minsize=self.minsize,
                            maxsize=self.maxsize,
                            pool_recycle=self.pool_recycle,
                            connect_timeout=self.connect_timeout,
                            autocommit=True
                        ),
                        timeout=10.0
                    )
                    
                    # 验证恢复后的连接池
                    if await asyncio.wait_for(self._test_pool_health(), timeout=5.0):
                        self.logger.info(f"✅ Pool recovery successful on attempt {attempt + 1}")
                        try:
                            await asyncio.wait_for(self._warmup_pool(), timeout=5.0)
                        except asyncio.TimeoutError:
                            self.logger.warning("Pool warmup timeout, but recovery successful")
                        return
                    else:
                        self.logger.warning(f"❌ Pool recovery health check failed on attempt {attempt + 1}")
                        
                except asyncio.TimeoutError:
                    self.logger.error(f"Pool recovery attempt {attempt + 1} timed out")
                    if self.pool:
                        try:
                            self.pool.close()
                        except:
                            pass
                        self.pool = None
                except Exception as e:
                    self.logger.error(f"Pool recovery error on attempt {attempt + 1}: {e}")
                    if self.pool:
                        try:
                            self.pool.close()
                            await asyncio.wait_for(self.pool.wait_closed(), timeout=2.0)
                        except Exception:
                            pass
                        finally:
                            self.pool = None
            
            self.logger.error("❌ Pool recovery failed after all attempts")
            self.pool = None
            
        finally:
            self.pool_recovering = False
```

连接池恢复流程采用了重试机制来应对暂时性的故障。系统最多尝试 3 次恢复操作，每次尝试之间有一定的延迟，给系统恢复的时间。恢复过程首先尝试优雅地关闭现有连接池，如果关闭操作超时则会强制清理。然后创建新的连接池，并进行健康验证。如果验证成功，还会执行连接池预热操作，确保新连接池能够立即投入使用。

恢复过程中使用了多个超时设置来防止操作无限期阻塞。连接池关闭超时为 3 秒，连接池创建超时为 10 秒，健康检查超时为 5 秒。这些超时值经过实践验证，能够覆盖正常操作所需的时间，同时在异常情况下快速失败。

### 5.4 连接释放与池管理

当应用程序使用完连接后，需要将连接释放回连接池。连接释放流程通过 `release_connection()` 方法实现，该方法负责将连接归还到池中或根据连接状态决定是否需要销毁连接。

```python
async def release_connection(self, session_id: str, connection: DorisConnection):
    """Release connection back to pool with proper error handling"""
    cached_conn = self.session_cache.get(session_id)
    if cached_conn:
        self.session_cache.remove(session_id)
        if not (cached_conn is connection):
            self.logger.warning("Invalid connection")
            connection = cached_conn

    if not connection or not connection.connection:
        self.logger.debug(f"No connection to release for session {session_id}")
        return
        
    try:
        # 检查连接池是否可用
        if not self.pool or self.pool.closed:
            self.logger.warning(f"Pool unavailable during release for session {session_id}, force closing connection")
            try:
                await connection.connection.ensure_closed()
            except Exception:
                pass
            return
        
        # 检查连接是否仍然有效
        if connection.connection.closed:
            self.logger.debug(f"Connection already closed, not releasing to pool")
            return
        
        # 释放连接到连接池
        self.pool.release(connection.connection)
        self.logger.debug(f"Connection released for session {session_id}")
        
    except Exception as e:
        self.logger.error(f"Error releasing connection: {e}")
        try:
            await connection.connection.ensure_closed()
        except Exception:
            pass
```

连接释放流程包含了多层验证和错误处理。首先检查连接是否来自会话缓存，确保释放的是正确的连接对象。然后验证连接池的可用性，如果连接池不可用则直接关闭连接而不是尝试释放。最后检查连接本身的状态，只有有效的连接才会被释放回池中。如果任何步骤发生异常，方法会尝试直接关闭连接，确保资源不会泄漏。

### 5.5 关闭管理器

当整个连接管理器需要关闭时，系统会执行一系列清理操作，确保所有资源被正确释放。关闭流程通过 `close()` 方法实现，该方法负责停止后台任务、关闭连接池和清理相关资源。

```python
async def close(self):
    """Close connection manager"""
    try:
        # 取消后台任务
        if self.pool_health_check_task:
            self.pool_health_check_task.cancel()
            try:
                await self.pool_health_check_task
            except asyncio.CancelledError:
                pass

        if self.pool_cleanup_task:
            self.pool_cleanup_task.cancel()
            try:
                await self.pool_cleanup_task
            except asyncio.CancelledError:
                pass

        # 关闭连接池
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

        self.logger.info("Connection manager closed successfully")

    except Exception as e:
        self.logger.error(f"Error closing connection manager: {e}")
```

关闭流程遵循了优雅关闭的原则。首先取消后台监控任务，等待它们正确完成终止处理。然后关闭连接池，等待所有连接安全释放。最后记录关闭完成的信息。任何异常都会被捕获并记录，确保关闭操作不会因异常而中断。

## 六、监控指标与诊断

### 6.1 指标收集

系统通过 `get_metrics()` 方法收集连接池的运行指标，这些指标反映了连接池的使用情况和性能特征。指标收集是监控系统的基础，为后续的诊断和告警提供数据支持。

```python
async def get_metrics(self) -> ConnectionMetrics:
    """Get connection pool metrics"""
    try:
        if self.pool:
            self.metrics.idle_connections = self.pool.freesize
            self.metrics.active_connections = self.pool.size - self.pool.freesize
        else:
            self.metrics.idle_connections = 0
            self.metrics.active_connections = 0
        
        return self.metrics
    except Exception as e:
        self.logger.error(f"Error getting metrics: {e}")
        return self.metrics
```

指标收集直接读取连接池的内部状态，包括池的总大小 `size` 和空闲连接数 `freesize`。活跃连接数通过总大小减去空闲连接数计算得出。这种实现方式简单高效，能够实时反映连接池的当前状态。

### 6.2 健康诊断

健康诊断功能通过 `diagnose_connection_health()` 方法提供，该方法对连接池状态进行全面检查并生成诊断结果。诊断结果包括池状态、池信息和优化建议，帮助运维人员快速了解系统状况。

```python
async def diagnose_connection_health(self) -> Dict[str, Any]:
    """Diagnose connection pool health"""
    diagnosis = {
        "timestamp": datetime.utcnow().isoformat(),
        "pool_status": "unknown",
        "pool_info": {},
        "recommendations": []
    }
    
    try:
        if not self.pool:
            diagnosis["pool_status"] = "not_initialized"
            diagnosis["recommendations"].append("Initialize connection pool")
            return diagnosis
        
        if self.pool.closed:
            diagnosis["pool_status"] = "closed"
            diagnosis["recommendations"].append("Recreate connection pool")
            return diagnosis
        
        diagnosis["pool_status"] = "healthy"
        diagnosis["pool_info"] = {
            "size": self.pool.size,
            "free_size": self.pool.freesize,
            "min_size": self.pool.minsize,
            "max_size": self.pool.maxsize
        }
        
        if self.pool.freesize == 0 and self.pool.size >= self.pool.maxsize:
            diagnosis["recommendations"].append("Connection pool exhausted - consider increasing max_connections")
        
        if await self._test_pool_health():
            diagnosis["pool_health"] = "healthy"
        else:
            diagnosis["pool_health"] = "unhealthy"
            diagnosis["recommendations"].append("Pool health check failed - may need recovery")
        
        return diagnosis
        
    except Exception as e:
        diagnosis["error"] = str(e)
        diagnosis["recommendations"].append("Manual intervention required")
        return diagnosis
```

健康诊断首先检查连接池的基本状态，包括是否已初始化和是否已关闭。然后收集连接池的配置信息和当前状态。最后执行实际的健康检查并根据结果生成相应的建议。诊断结果涵盖了连接池的各个方面，为问题排查提供了全面的信息。

### 6.3 健康报告生成

健康报告生成功能通过 `generate_health_report()` 方法实现，该方法将诊断信息整合为结构化的报告格式。报告不仅包含当前状态，还包括基于数据分析的优化建议。

```python
async def generate_health_report(self) -> dict[str, Any]:
    """Generate connection health report"""
    pool_status = await self.get_pool_status()
    
    # 计算连接池利用率
    pool_utilization = 1.0 - (pool_status["free_connections"] / pool_status["pool_size"]) if pool_status["pool_size"] > 0 else 0.0
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "pool_status": pool_status,
        "pool_utilization": pool_utilization,
        "recommendations": [],
    }
    
    # 基于池状态生成建议
    if pool_status["connection_errors"] > 10:
        report["recommendations"].append("High connection error rate detected, review connection configuration")
    
    if pool_utilization > 0.9:
        report["recommendations"].append("Connection pool utilization is high, consider increasing pool size")
    
    if pool_status["free_connections"] == 0:
        report["recommendations"].append("No free connections available, consider increasing pool size")
    
    return report
```

健康报告的核心指标是连接池利用率，它反映了当前活跃连接占池容量的比例。基于利用率和其他指标，报告会生成相应的优化建议。当错误数超过阈值、利用率过高或无空闲连接时，报告会建议相应的优化措施。这些建议帮助运维人员主动发现和解决潜在问题。

## 七、总结

本文档详细介绍了 Doris MCP Server 连接池监控体系的设计与实现。该监控体系通过多层次的健康检查机制、主动式的无效连接清理和自动化的故障恢复流程，确保了数据库连接的高可用性和稳定性。系统采用后台异步任务的方式执行监控操作，对正常业务运行的影响降到最低。同时，丰富的诊断和报告功能为运维工作提供了有力支持，帮助快速定位和解决连接相关问题。该监控体系的设计遵循了可靠性、实时性和可维护性的原则，是 Doris MCP Server 稳定运行的重要保障。
