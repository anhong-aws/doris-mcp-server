# 实现MCP统计数据固化功能（关闭服务时保存）

## 任务描述
将MCP方法调用统计数据固化到文件中，在服务启动时加载，并在服务关闭时保存，确保数据不会丢失。

## 实现方案

### 核心思路
1. 在类首次使用时，从文件加载历史统计数据
2. 在服务关闭时，将当前统计数据保存到文件
3. 使用JSON格式存储，便于查看和管理
4. 确保文件操作的线程安全性

## 实现步骤

1. **修改mcp_call_stats.py文件**：
   - 添加`_STATS_FILE_PATH`常量，默认保存到`logs/mcp_call_stats.json`
   - 添加`_ensure_stats_loaded`类方法，用于确保统计数据已加载
   - 添加`load_stats()`类方法，用于从文件加载统计数据
   - 添加`save_stats()`类方法，用于将统计数据保存到文件
   - 在关键方法（如`increment_call_count`）中调用`_ensure_stats_loaded()`确保数据已加载
   - 在模块级别添加`_ensure_stats_loaded()`调用，确保类导入时数据即加载

2. **修改main.py文件**：
   - 在服务关闭逻辑中添加对`MCPCallStats.save_stats()`的调用
   - 确保在HTTP模式和stdio模式下都能正确保存数据

3. **确保日志目录存在**：
   - 在文件操作前检查并创建日志目录

## 技术要点
- 使用类方法和类变量实现全局统计数据管理
- 使用threading.RLock确保线程安全
- 使用try-except处理文件操作异常
- 确保在服务关闭时正确调用保存方法
- 在类首次使用时自动加载历史数据

## 预期效果
- 服务启动时，自动从`logs/mcp_call_stats.json`加载历史统计数据
- 服务关闭时，自动将当前统计数据保存到`logs/mcp_call_stats.json`
- 即使服务意外崩溃，之前保存的数据也不会丢失
- 统计数据文件采用JSON格式，便于查看和分析

## 代码修改点
1. `doris_mcp_server/utils/mcp_call_stats.py`：添加文件加载和保存功能
2. `doris_mcp_server/main.py`：在服务关闭时调用保存方法