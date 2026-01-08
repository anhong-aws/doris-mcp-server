# 实现MCP日志文件和方法调用统计功能

## 1. 日志系统扩展

### 1.1 添加MCP专用日志处理器
- 在 `DorisLoggerManager.setup_logging` 方法中添加一个专门的MCP日志处理器
- 配置MCP日志文件路径为 `logs/doris_mcp_server_mcp.log`
- 使用与现有日志相同的轮转策略

### 1.2 实现MCP日志记录器
- 添加 `get_mcp_logger()` 函数，用于获取MCP专用日志记录器
- 确保MCP日志独立于其他日志，便于单独查看

## 2. 方法调用统计功能

### 2.1 创建独立的统计模块
- 创建新文件 `doris_mcp_server/utils/mcp_call_stats.py`
- 定义 `MCPCallStats` 类，包含类变量和计数方法
- 实现线程安全的调用统计功能

### 2.2 统计类设计
- 类变量 `_call_stats`：记录每天每个方法的调用次数
- 字典结构：`_call_stats = {"2024-01-08": {"method1": 10, "method2": 20}}`
- 方法 `increment_call_count(method_name)`：增加指定方法的调用次数
- 方法 `get_daily_stats(date_str)`：获取指定日期的统计数据
- 方法 `get_total_stats()`：获取所有日期的统计数据
- 方法 `cleanup_old_stats()`：清理超过三个月的统计数据

### 2.3 自动清理机制
- 在 `increment_call_count` 方法中调用 `cleanup_old_stats()`
- 每次调用方法时检查并清理过期数据
- 清理逻辑：删除超过当前日期三个月的统计数据

### 2.4 集成到工具调用流程
- 在 `ToolsManager` 类中导入 `MCPCallStats` 类
- 在 `call_tool` 方法中调用 `MCPCallStats.increment_call_count()` 方法
- 确保所有工具调用都被统计到

## 3. 实现步骤

1. 修改 `logger.py`，添加MCP日志处理器和记录器
2. 创建 `mcp_call_stats.py`，实现调用统计和自动清理功能
3. 修改 `tools_manager.py`，集成调用统计功能
4. 测试基本功能

## 文件修改清单

- `doris_mcp_server/utils/logger.py` - 添加MCP日志支持
- `doris_mcp_server/utils/mcp_call_stats.py` - 实现调用统计和自动清理功能
- `doris_mcp_server/tools/tools_manager.py` - 集成调用统计功能