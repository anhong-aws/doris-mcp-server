# Doris MCP 协议分析：main.py 与 tools_manager.py 关联

## 1. 概述

本文档分析 Doris MCP Server 中 `main.py` 和 `tools_manager.py` 之间的关联，重点关注 MCP（Model Context Protocol）协议的实现，特别是 `@mcp.tool` 装饰器和 `list_tools` 方法之间的关系与代码重复问题。

## 2. MCP 协议基础

MCP 是一个用于 AI 模型与外部工具/服务交互的协议，允许模型发现、调用和使用外部工具。Doris MCP Server 实现了该协议，提供了与 Doris 数据库交互的工具集。

## 3. 核心组件与关联

### 3.1 `tools_manager.py` 中的关键组件

#### 3.1.1 `register_tools_with_mcp` 方法 
 
 **功能**：将所有工具注册到 MCP 服务器（**注意：此方法在当前代码中未被调用，可能是遗留代码或备用实现**） 
 
 **实现方式**：使用 `@mcp.tool` 装饰器定义工具 
 
 **代码分析**：
经过全面搜索和分析，我确认 `register_tools_with_mcp` 方法在当前代码库中**并没有被调用**。这意味着这个方法可能是：
1. 遗留代码：在早期版本中使用，后来被新的实现方式替代
2. 备用实现：为不同的 MCP 服务器集成方式准备的
3. 未完成的功能：计划实现但尚未整合到主流程中

 **实际工具注册与调用流程**：
在当前的 Doris MCP Server 实现中，工具注册和调用是通过以下机制实现的：

1. **工具定义**：工具在 `DorisToolsManager` 类中通过两种方式定义：
   - `list_tools` 方法：返回 `Tool` 对象列表，定义了工具的元数据（名称、描述、参数）
   - `call_tool` 方法：根据工具名称执行相应的工具逻辑

2. **工具注册**：在 `DorisServer` 类的 `_setup_handlers` 方法中，通过以下步骤完成工具注册：
   ```python
   def _setup_handlers(self):
       # 设置资源、工具和提示的列表与调用处理函数
       self.server.resources = self.resources_manager.list_resources()
       self.server.tools = self.tools_manager.list_tools()  # <-- 工具在这里注册
       self.server.prompts = self.prompts_manager.list_prompts()
       
       # 注册工具调用处理函数
       async def handle_list_tools():
           return await self.tools_manager.list_tools()
       
       # 其他处理函数注册...
   ```

3. **工具调用**：当客户端请求调用工具时，MCP 框架会调用相应的处理函数，最终通过 `call_tool` 方法执行工具逻辑

这种实现方式与 `register_tools_with_mcp` 方法中使用的 `@mcp.tool` 装饰器方式不同，但同样能够完成工具的注册和调用功能。

 **示例代码**：
```python
async def register_tools_with_mcp(self, mcp):
    """Register all tools to MCP server"""
    logger.info("Starting to register MCP tools")

    # SQL query execution tool
    @mcp.tool(
        "exec_query",
        description="[Function Description]: Execute SQL query and return result command...",
    )
    async def exec_query_tool(
        sql: str,
        db_name: str = None,
        catalog_name: str = None,
        max_rows: int = 100,
        timeout: int = 30,
    ) -> str:
        """Execute SQL query (supports federation queries)"""
        return await self.call_tool("exec_query", {
            "sql": sql,
            "db_name": db_name,
            "catalog_name": catalog_name,
            "max_rows": max_rows,
            "timeout": timeout
        })
    
    # 其他工具注册...
```

#### 3.1.2 `list_tools` 方法

**功能**：返回所有可用查询工具的列表（注释中提到主要用于 stdio 模式）

**实现方式**：手动创建 `Tool` 对象列表

**示例代码**：
```python
async def list_tools(self) -> List[Tool]:
    """List all available query tools (for stdio mode)"""
    adbc_config = self.connection_manager.config.adbc
    
    tools = [
        Tool(
            name="exec_query",
            description="[Function Description]: Execute SQL query and return result command...",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL statement to execute, must use three-part naming"},
                    "db_name": {"type": "string", "description": "Database name"},
                    "catalog_name": {"type": "string", "description": "Catalog name"},
                    "max_rows": {"type": "integer", "description": "Maximum number of rows to return", "default": 100},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
                },
                "required": ["sql"],
            },
        ),
        # 其他 Tool 对象...
    ]
    return tools
```

### 3.2 `main.py` 中的关键组件

#### 3.2.1 MCP 服务器设置

在 `DorisServer` 类的 `_setup_handlers` 方法中，设置了工具相关的处理器：

```python
@self.server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Handle tool list request"""
    try:
        self.logger.info("Handling tool list request")
        tools = await self.tools_manager.list_tools()
        self.logger.info(f"Returning {len(tools)} tools")
        return tools
    except Exception as e:
        self.logger.error(f"Failed to handle tool list request: {e}")
        return []
```

## 4. 代码重复问题分析

### 4.1 问题描述

从代码中可以看到，`register_tools_with_mcp` 方法和 `list_tools` 方法之间存在潜在的代码重复：

1. **工具描述重复**：同一个工具的描述在两个地方都有定义
2. **工具参数重复**：工具的参数信息在两个地方都有定义
3. **工具数量重复**：如果两个方法都被使用，每当添加或修改一个工具时，需要在两个地方都进行修改

**重要说明**：由于 `register_tools_with_mcp` 方法实际上并未被调用，这种代码重复目前并没有影响到实际的系统功能，但它确实增加了代码维护的复杂性和潜在风险。

### 4.2 代码重复的原因

1. **历史原因**：注释中提到 `list_tools` 方法最初是为 stdio 模式设计的，而 `register_tools_with_mcp` 可能是为 HTTP 模式或其他集成方式设计的
2. **架构设计**：MCP 协议支持多种工具注册方式，`@mcp.tool` 装饰器和工具列表查询是两个不同的概念
3. **实现方式**：当前实现中，工具注册和工具列表查询使用了不同的机制，导致了代码重复
4. **代码演进**：系统可能经历了架构变更，但旧的实现代码未被完全清理

### 4.3 代码重复的影响

1. **维护困难**：修改一个工具需要在两个地方进行相同的修改
2. **一致性问题**：容易出现两个地方的工具定义不一致
3. **代码冗余**：增加了代码量和理解难度

## 5. MCP 协议中的工具处理流程

### 5.1 工具注册流程

1. `DorisServer` 初始化时创建 `DorisToolsManager` 实例
2. 在 `start_stdio` 或 `start_http` 方法中调用 `register_tools_with_mcp`
3. 使用 `@mcp.tool` 装饰器将工具注册到 MCP 服务器
4. 每个工具都有对应的处理函数，调用 `call_tool` 方法执行实际业务逻辑

### 5.2 工具列表查询流程

1. 客户端发送工具列表查询请求
2. MCP 服务器调用 `handle_list_tools` 函数
3. `handle_list_tools` 调用 `tools_manager.list_tools()` 获取工具列表
4. `list_tools` 方法返回手动创建的 `Tool` 对象列表
5. MCP 服务器将工具列表返回给客户端

### 5.3 工具调用流程

1. 客户端发送工具调用请求
2. MCP 服务器根据工具名称找到对应的处理函数
3. 处理函数调用 `call_tool` 方法执行实际业务逻辑
4. `call_tool` 方法根据工具名称调用对应的业务逻辑处理器
5. 将处理结果返回给客户端

## 6. 代码重复问题的解决方案

考虑到 `register_tools_with_mcp` 方法在当前代码中实际上并未被调用，代码重复问题的解决方案可以更加简洁和直接。

### 6.1 方案一：删除未使用的 `register_tools_with_mcp` 方法

**思路**：由于 `register_tools_with_mcp` 方法未被调用，直接删除这个方法可以消除代码重复问题。

**实现方式**：
1. 删除 `DorisToolsManager` 类中的 `register_tools_with_mcp` 方法
2. 更新相关文档和注释

**优点**：
- 简单直接，立即消除代码重复
- 减少维护成本
- 代码更加简洁清晰

**缺点**：
- 如果未来需要使用 `@mcp.tool` 装饰器方式注册工具，需要重新实现

### 6.2 方案二：统一工具定义来源

**思路**：创建一个统一的工具定义列表，然后从这个列表生成 `list_tools` 方法的返回值，同时保留 `register_tools_with_mcp` 方法作为可选的注册方式。

**实现方式**：
```python
# 统一的工具定义
_TOOL_DEFINITIONS = [
    {
        "name": "exec_query",
        "description": "[Function Description]: Execute SQL query and return result command...",
        "parameters": {
            "sql": {"type": "string", "required": True, "description": "SQL statement to execute"},
            "db_name": {"type": "string", "required": False, "description": "Database name"},
            "catalog_name": {"type": "string", "required": False, "description": "Catalog name"},
            "max_rows": {"type": "integer", "required": False, "default": 100, "description": "Maximum number of rows to return"},
            "timeout": {"type": "integer", "required": False, "default": 30, "description": "Timeout in seconds"},
        }
    },
    # 其他工具定义...
]

async def register_tools_with_mcp(self, mcp):
    """Register all tools to MCP server (optional)"""
    for tool_def in _TOOL_DEFINITIONS:
        @mcp.tool(tool_def["name"], description=tool_def["description"])
        async def tool_handler(**kwargs):
            return await self.call_tool(tool_def["name"], kwargs)
        
        # 动态设置函数参数
        import inspect
        sig = inspect.signature(tool_handler)
        params = [
            inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD, 
                             default=param.get("default", inspect.Parameter.empty))
            for name, param in tool_def["parameters"].items()
        ]
        tool_handler.__signature__ = sig.replace(parameters=params)

async def list_tools(self) -> List[Tool]:
    """List all available query tools"""
    tools = []
    for tool_def in _TOOL_DEFINITIONS:
        # 构建 inputSchema
        input_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for name, param in tool_def["parameters"].items():
            input_schema["properties"][name] = {
                "type": param["type"],
                "description": param["description"]
            }
            if "default" in param:
                input_schema["properties"][name]["default"] = param["default"]
            
            if param.get("required", False):
                input_schema["required"].append(name)
        
        tools.append(Tool(
            name=tool_def["name"],
            description=tool_def["description"],
            inputSchema=input_schema
        ))
    
    return tools
```

**优点**：
- 消除代码重复
- 保持代码的灵活性，可以选择使用不同的工具注册方式
- 便于未来扩展和维护

**缺点**：
- 增加了代码的复杂度
- 需要额外的测试来确保两种注册方式的一致性

### 6.3 方案三：从 MCP 服务器获取工具列表（如果未来使用）

**思路**：如果未来决定使用 `@mcp.tool` 装饰器方式注册工具，可以利用 MCP 服务器的内部机制，直接获取已注册的工具列表。

**实现方式**：
```python
async def list_tools(self) -> List[Tool]:
    """List all available query tools"""
    # 从 MCP 服务器获取已注册的工具列表
    # 具体实现取决于 MCP 库的内部 API
    return self.mcp.get_registered_tools()
```

**优点**：
- 直接利用 MCP 服务器的内部机制
- 避免手动维护工具列表

**缺点**：
- 依赖 MCP 库的内部 API，可能会因版本变化而失效
- 目前不适用，因为未使用 `@mcp.tool` 装饰器方式

## 7. 总结

经过全面分析，我发现 Doris MCP Server 中的 `register_tools_with_mcp` 方法和 `list_tools` 方法之间的关系有以下特点：

1. **`register_tools_with_mcp` 方法**：
   - 使用 `@mcp.tool` 装饰器定义工具
   - 在当前代码库中**并未被调用**
   - 可能是遗留代码、备用实现或未完成的功能

2. **`list_tools` 方法**：
   - 返回 `Tool` 对象列表，定义了工具的元数据
   - 在 `DorisServer` 类的 `_setup_handlers` 方法中被调用
   - 是当前实现中工具注册和查询的核心机制

3. **代码重复问题**：
   - 由于 `register_tools_with_mcp` 方法未被调用，代码重复问题目前并未影响系统功能
   - 但未使用的代码增加了维护成本和理解难度

4. **实际工具注册与调用流程**：
   - 工具通过 `list_tools` 方法定义元数据
   - 在 `DorisServer._setup_handlers` 中注册到 MCP 服务器
   - 工具调用通过 `call_tool` 方法执行实际逻辑

## 8. 建议

基于以上分析，我提出以下建议：

1. **采用方案一**：删除未使用的 `register_tools_with_mcp` 方法
   - 这是最直接和有效的解决方案
   - 可以立即消除代码重复问题
   - 提高代码的可维护性和清晰度

2. **修改注释**：
   - 更新 `list_tools` 方法的注释，明确说明它是工具定义的唯一来源
   - 移除或更新关于 `register_tools_with_mcp` 方法的过时文档

3. **代码优化**：
   - 考虑统一工具定义的格式，使其更加清晰和易于维护
   - 为 `list_tools` 方法添加更多的错误处理和日志记录

4. **未来扩展**：
   - 如果未来需要支持 `@mcp.tool` 装饰器方式，可以基于当前的 `list_tools` 方法重新实现
   - 考虑添加配置选项，允许用户选择使用不同的工具注册方式

5. **测试和文档**：
   - 添加测试确保 `list_tools` 方法的正确性
   - 更新文档，明确说明当前的工具注册和调用机制

通过以上建议，可以解决当前代码中的潜在问题，提高系统的可维护性和扩展性。