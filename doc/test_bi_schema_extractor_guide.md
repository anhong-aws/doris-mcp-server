# BI Schema Extractor 单元测试指南

本指南旨在帮助理解 `test_bi_schema_extractor.py` 文件中的 Python 单元测试代码。这是一个针对 Doris MCP Server 中 `bi_schema_extractor.py` 的 `get_table_schema_for_mcp` 方法的单元测试文件。

## 1. 测试文件基本结构

```python
#!/usr/bin/env python3
# 版权声明和许可证信息

import pytest
from unittest.mock import Mock, AsyncMock, patch

from doris_mcp_server.utils.bi_schema_extractor import MetadataExtractor
from doris_mcp_server.utils.sql_security_utils import SQLSecurityError

class TestBiSchemaExtractor:
    """BI Schema Extractor 单元测试类"""
    
    @pytest.fixture
    def mock_connection_manager(self):
        """创建模拟的连接管理器"""
        return Mock()

    @pytest.fixture
    def metadata_extractor(self, mock_connection_manager):
        """创建 MetadataExtractor 实例"""
        return MetadataExtractor(
            db_name="test_db",
            catalog_name="internal",
            connection_manager=mock_connection_manager
        )
    
    # 各个测试用例...
```

### 1.1 导入语句
- `pytest`: Python 单元测试框架
- `unittest.mock`: 用于模拟对象和方法
- `MetadataExtractor`: 被测试的类
- `SQLSecurityError`: 用于测试安全验证失败的情况

### 1.2 测试类
- `TestBiSchemaExtractor`: 包含所有测试用例的类，命名遵循 `Test + 被测试类名` 的约定

### 1.3 测试 Fixture
- `mock_connection_manager`: 创建一个模拟的连接管理器对象
- `metadata_extractor`: 使用模拟的连接管理器创建一个 `MetadataExtractor` 实例，供所有测试用例使用

## 2. 测试用例详解

### 2.1 成功获取表结构测试

```python
@pytest.mark.asyncio
async def test_get_table_schema_for_mcp_success(self, metadata_extractor):
    """测试成功获取表结构"""
    # 创建模拟的表结构数据
    mock_schema = [
        {
            "COLUMN_NAME": "id",
            "DATA_TYPE": "int(11)",
            "IS_NULLABLE": "NO",
            "COLUMN_DEFAULT": None,
            "COLUMN_COMMENT": "User ID",
            "ORDINAL_POSITION": 1,
            "COLUMN_KEY": "PRI",
            "EXTRA": "auto_increment"
        },
        {
            "COLUMN_NAME": "name",
            "DATA_TYPE": "varchar(100)",
            "IS_NULLABLE": "YES",
            "COLUMN_DEFAULT": None,
            "COLUMN_COMMENT": "User name",
            "ORDINAL_POSITION": 2,
            "COLUMN_KEY": "",
            "EXTRA": ""
        }
    ]
    
    # 模拟 get_table_schema_async 方法的返回值
    with patch.object(metadata_extractor, 'get_table_schema_async') as mock_get_schema:
        mock_get_schema.return_value = mock_schema
        
        # 调用被测试的方法
        result = await metadata_extractor.get_table_schema_for_mcp(
            table_name="users",
            db_name="test_db",
            catalog_name="internal"
        )
        
        # 验证结果
        assert result["success"] is True
        assert "result" in result
        assert result["result"] == mock_schema
        mock_get_schema.assert_called_once_with(
            table_name="users",
            db_name="test_db",
            catalog_name="internal"
        )
```

**关键点解释：**
- `@pytest.mark.asyncio`: 标记这是一个异步测试用例
- `mock_schema`: 模拟的表结构数据，模拟从数据库获取的真实表结构
- `patch.object`: 模拟 `get_table_schema_async` 方法，使其返回预设的 `mock_schema`
- `assert`: 验证测试结果是否符合预期
- `mock_get_schema.assert_called_once_with`: 验证模拟方法被正确调用了一次

### 2.2 参数缺失测试

```python
@pytest.mark.asyncio
async def test_get_table_schema_for_mcp_missing_table_name(self, metadata_extractor):
    """测试缺少 table_name 参数"""
    # 调用方法时不提供有效的 table_name
    result = await metadata_extractor.get_table_schema_for_mcp(
        table_name="",
        db_name="test_db",
        catalog_name="internal"
    )
    
    # 验证结果
    assert result["success"] is False
    assert result["error"] == "Missing table_name parameter"
```

**关键点解释：**
- 测试当 `table_name` 参数为空时的错误处理
- 验证返回的错误信息是否正确

### 2.3 安全验证测试

```python
@pytest.mark.asyncio
async def test_get_table_schema_for_mcp_invalid_table_name(self, metadata_extractor):
    """测试无效的表名"""
    # 模拟 validate_identifier 函数抛出异常
    with patch('doris_mcp_server.utils.bi_schema_extractor.validate_identifier') as mock_validate:
        mock_validate.side_effect = SQLSecurityError("Invalid table name")
        
        # 调用方法
        result = await metadata_extractor.get_table_schema_for_mcp(
            table_name="invalid-table-name",
            db_name="test_db",
            catalog_name="internal"
        )
        
        # 验证结果
        assert result["success"] is False
        assert "Invalid table name: invalid-table-name" in result["error"]
        assert "Table name contains invalid characters" in result["message"]
```

**关键点解释：**
- `mock_validate.side_effect`: 模拟函数抛出异常的情况
- 测试安全验证机制是否正常工作
- 验证错误信息的格式和内容

### 2.4 默认参数测试

```python
@pytest.mark.asyncio
async def test_get_table_schema_for_mcp_default_params(self, metadata_extractor):
    """测试使用默认参数"""
    # 创建模拟的表结构数据
    mock_schema = [
        {
            "COLUMN_NAME": "id",
            "DATA_TYPE": "int(11)",
            "IS_NULLABLE": "NO",
            "COLUMN_DEFAULT": None,
            "COLUMN_COMMENT": "User ID",
            "ORDINAL_POSITION": 1,
            "COLUMN_KEY": "PRI",
            "EXTRA": "auto_increment"
        }
    ]
    
    with patch.object(metadata_extractor, 'get_table_schema_async') as mock_get_schema:
        mock_get_schema.return_value = mock_schema
        
        # 只提供 table_name 参数，其他参数使用默认值
        result = await metadata_extractor.get_table_schema_for_mcp(
            table_name="users"
        )
        
        # 验证结果
        assert result["success"] is True
        mock_get_schema.assert_called_once_with(
            table_name="users",
            db_name=None,
            catalog_name=None
        )
```

**关键点解释：**
- 测试当只提供 `table_name` 参数时的行为
- 验证默认参数是否被正确传递

## 3. 单元测试核心概念

### 3.1 模拟（Mock）
模拟是单元测试中的核心概念，用于替代真实对象或方法的行为，以便于测试特定场景。模拟可以：
- 控制外部依赖的行为
- 避免实际执行耗时或有副作用的操作
- 模拟各种返回值和异常情况

#### 3.1.1 `with patch.object()` 语句详解
```python
with patch.object(metadata_extractor, 'get_table_schema_async') as mock_get_schema:
    mock_get_schema.return_value = mock_schema
    # 测试代码
```
- **`with`语句**：Python的上下文管理器，用于临时替换对象属性，执行完毕后自动恢复原始状态
- **`patch.object()`函数**：来自`unittest.mock`，用于替换对象的特定方法或属性
  - **替换内容**：`patch.object(metadata_extractor, 'get_table_schema_async')`将`metadata_extractor`对象的`get_table_schema_async`方法临时替换为一个Mock对象
  - **是否真正执行**：被替换的`get_table_schema_async`方法**不会**被真正执行，而是由Mock对象代替执行
  - **恢复机制**：当`with`语句块执行完毕后，`get_table_schema_async`方法会自动恢复为原始方法
- **`as mock_get_schema`**：将替换后的模拟对象赋值给`mock_get_schema`变量，以便我们可以配置和验证它
  - **mock_get_schema的类**：`mock_get_schema`是`unittest.mock.Mock`类的实例，这是Python标准库中用于创建模拟对象的核心类
  - **Mock类的主要作用**：模拟Python对象的行为，用于替换真实对象进行测试
- **`mock_get_schema.return_value`**：设置模拟对象被调用时的返回值，模拟真实方法的返回结果

### Mock对象的主要属性和方法

`mock_get_schema`作为`Mock`类的实例，具有以下常用属性和方法：

#### 配置模拟行为的属性
1. **`return_value`**：
   - 设置模拟方法被调用时的返回值
   - 可以是任何Python对象（如字典、列表、类实例等）
   - 示例：`mock_get_schema.return_value = {"column_name": "id"}`

2. **`side_effect`**：
   - 设置模拟方法被调用时的副作用
   - 可以是异常（用于测试错误处理）、可迭代对象（每次调用返回不同值）或函数（自定义返回逻辑）
   - 示例：`mock_get_schema.side_effect = Exception("Database error")`

3. **`spec`/`spec_set`**：
   - 限制模拟对象只能有指定类的属性和方法
   - 用于确保测试代码与真实对象的接口保持一致

#### 验证模拟调用的方法
1. **`assert_called()`**：
   - 断言模拟方法至少被调用过一次

2. **`assert_called_once()`**：
   - 断言模拟方法恰好被调用过一次

3. **`assert_called_with(*args, **kwargs)`**：
   - 断言模拟方法被调用时使用了指定的参数
   - 示例：`mock_get_schema.assert_called_with(table_name="users", db_name="test_db")`

4. **`assert_called_once_with(*args, **kwargs)`**：
   - 断言模拟方法恰好被调用过一次，并且使用了指定的参数

5. **`assert_any_call(*args, **kwargs)`**：
   - 断言模拟方法在多次调用中至少有一次使用了指定的参数

6. **`reset_mock()`**：
   - 重置模拟对象的调用历史和配置
   - 用于在同一个测试用例中重用模拟对象

#### 获取调用信息的属性
1. **`call_count`**：
   - 获取模拟方法被调用的次数

2. **`call_args`**：
   - 获取最后一次调用的参数
   - 返回一个`call`对象，包含位置参数和关键字参数

3. **`call_args_list`**：
   - 获取所有调用的参数列表
   - 返回`call`对象的列表

4. **`method_calls`**：
   - 获取模拟对象上所有方法调用的列表
   - 用于验证链式调用

这些属性和方法使得`Mock`对象非常灵活，可以满足各种测试场景的需求。通过配置和验证模拟对象，我们可以精确地控制测试环境，确保测试的准确性和可靠性。

#### 3.1.2 Mock对象的`return_value`
- Mock对象的`return_value`属性用于定义当模拟方法被调用时应该返回什么值
- 这允许我们模拟依赖方法的行为，而不需要实际执行它
- 例如：`mock_get_schema.return_value = mock_schema` 表示当`get_table_schema_async`被调用时，返回`mock_schema`数据

#### 3.1.3 如何验证是否进入了实际方法
要确认代码是否进入了`get_table_schema_for_mcp`内部执行，可以通过以下方式：

1. **查看日志输出**：`get_table_schema_for_mcp`方法开头有`logger.info()`日志
2. **添加断言**：验证方法返回了预期结果（如`assert result["success"] is True`）
3. **检查方法内部逻辑**：如果方法内部有特定的条件分支（如参数验证），可以通过测试不同参数组合来验证
4. **使用调试器**：在方法内部设置断点，运行测试时检查是否触发断点

### 3.2 单元测试策略：测试内部方法的重要性

### 为什么需要单独测试内部方法

用户可能会问："既然 `get_table_schema_for_mcp` 已经调用了 `get_table_schema_async`，为什么不能在测试 `get_table_schema_for_mcp` 时顺便测试 `get_table_schema_async`？"

这涉及到单元测试的核心原则和 Mock 的使用目的：

1. **单元测试的隔离性原则**：
   - 单元测试应该专注于测试单个单元的功能，而不依赖于其他单元的实现
   - 当我们在 `test_get_table_schema_for_mcp_success` 中使用 `patch.object` Mock 掉 `get_table_schema_async` 时，我们实际上是在**隔离** `get_table_schema_for_mcp` 的测试，使其不依赖于 `get_table_schema_async` 的实际实现
   - 这种隔离使得测试更可控、更稳定，因为它只关注 `get_table_schema_for_mcp` 如何处理输入和输出，而不关心内部调用的方法如何实现

2. **Mock 的作用**：
   - Mock 的主要目的是**替代依赖**，而不是测试依赖本身
   - 当我们在 `test_get_table_schema_for_mcp_success` 中 Mock 掉 `get_table_schema_async` 时，我们是在假设 `get_table_schema_async` 已经正常工作的前提下，测试 `get_table_schema_for_mcp` 的功能
   - 如果我们不在这个测试中 Mock `get_table_schema_async`，那么这个测试就变成了一个**集成测试**，它会同时测试 `get_table_schema_for_mcp` 和 `get_table_schema_async` 两个方法

3. **内部方法的复杂性**：
   - `get_table_schema_async` 方法本身可能包含复杂的业务逻辑，比如处理不同数据库、解析复杂的元数据等
   - 如果一个内部方法被多个外部方法调用，那么为它编写专门的单元测试可以确保它在各种情况下都能正常工作
   - 单独测试内部方法还可以更容易地覆盖边缘情况和异常处理逻辑

通过为 `get_table_schema_async` 编写专门的单元测试（如 `test_get_table_schema_async`），我们可以：
- 确保 `get_table_schema_async` 本身的功能正确性
- 提高代码覆盖率
- 更容易地定位和修复问题
- 使测试更模块化、更易于维护

### 3.3 VSCode单元测试调试配置

为了方便在VSCode中调试单元测试，我们需要配置调试环境。以下是详细的配置步骤和使用方法：

#### 3.2.1 调试配置文件

项目中已经创建了`.vscode`目录，包含以下配置文件：

**1. `.vscode/launch.json` - 调试器配置**

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: pytest - All Tests",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/.venv/bin/pytest",
            "args": ["-xvs", "test/"],
            "console": "integratedTerminal",
            "justMyCode": false,
            "workingDirectory": "${workspaceFolder}"
        },
        {
            "name": "Python Debugger: pytest - Single Test",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/.venv/bin/pytest",
            "args": ["-xvs", "${file}", "::${selectedText}"],
            "console": "integratedTerminal",
            "justMyCode": false,
            "workingDirectory": "${workspaceFolder}"
        },
        {
            "name": "Python Debugger: pytest - bi_schema_extractor",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/.venv/bin/pytest",
            "args": ["-xvs", "test/utils/test_bi_schema_extractor.py"],
            "console": "integratedTerminal",
            "justMyCode": false,
            "workingDirectory": "${workspaceFolder}"
        },
        {
            "name": "Python Debugger: pytest - Specific Function",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/.venv/bin/pytest",
            "args": ["-xvs", "test/utils/test_bi_schema_extractor.py::test_get_table_schema_async"],
            "console": "integratedTerminal",
            "justMyCode": false,
            "workingDirectory": "${workspaceFolder}"
        }
    ]
}
```

**2. `.vscode/tasks.json` - 任务配置**

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "selectPythonTest",
            "type": "shell",
            "command": "echo 'Select a test function to debug'",
            "presentation": {
                "echo": true,
                "reveal": "silent",
                "focus": false,
                "panel": "shared",
                "showReuseMessage": false,
                "clear": false
            }
        },
        {
            "label": "pytest: Run All Tests",
            "type": "shell",
            "command": "${workspaceFolder}/.venv/bin/pytest",
            "args": ["-xvs", "test/"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "dedicated",
                "showReuseMessage": true,
                "clear": false
            },
            "problemMatcher": [
                {
                    "owner": "python",
                    "pattern": {
                        "regexp": "^(.*?):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                        "file": 1,
                        "line": 2,
                        "column": 3,
                        "severity": 4,
                        "message": 5
                    }
                }
            ]
        }
    ]
}
```

#### 3.2.2 调试方法

1. **启动调试**
   - 打开VSCode的调试面板（Ctrl+Shift+D或Cmd+Shift+D）
   - 在调试配置下拉菜单中选择一个调试配置
   - 点击绿色的"开始调试"按钮（F5）

2. **调试特定测试函数**
   - 打开测试文件（如`test/utils/test_bi_schema_extractor.py`）
   - 选择要调试的测试函数名称（如`test_get_table_schema_async`）
   - 使用"Python Debugger: pytest - Single Test"配置启动调试

3. **调试单个测试文件**
   - 打开要调试的测试文件
   - 使用"Python Debugger: pytest - bi_schema_extractor"配置启动调试

4. **调试所有测试**
   - 使用"Python Debugger: pytest - All Tests"配置启动调试

#### 3.2.3 调试技巧

1. **设置断点**
   - 在代码行号左侧单击即可设置断点
   - 断点会在调试过程中暂停执行，方便查看变量和执行流程

2. **查看变量**
   - 调试暂停时，可以在"变量"面板中查看当前作用域的变量值
   - 可以将鼠标悬停在代码中的变量上查看其值

3. **控制执行**
   - **继续执行**：F5
   - **单步跳过**：F10
   - **单步进入**：F11
   - **单步跳出**：Shift+F11
   - **暂停执行**：Ctrl+F5
   - **停止执行**：Shift+F5

#### 3.2.4 终端配置文件加载问题解决方案

**问题描述**：VSCode 中终端的 `.zshrc` 文件还没加载完就执行测试命令，导致环境变量和配置未正确初始化。

**根本原因**：默认情况下，VSCode 启动终端时不会以登录 shell 方式运行，导致 `.zshrc` 中的部分配置未完全加载。

**解决方案**：

1. **在项目中创建 VSCode 设置文件**：
   在 `.vscode/settings.json` 中添加以下配置：
   ```json
   {
       "terminal.integrated.automationProfile.osx": {
           "path": "/bin/zsh",
           "args": ["-l"]
       },
       "terminal.integrated.defaultProfile.osx": "zsh",
       "terminal.integrated.inheritEnv": true,
       "terminal.integrated.profiles.osx": {
           "zsh": {
               "path": "/bin/zsh",
               "args": ["-l"]
           }
       }
   }
   ```

2. **关键配置说明**：
   - `"args": ["-l"]`: 使 zsh 以登录 shell 方式运行，确保完整加载 `.zshrc` 文件
   - `"inheritEnv": true`: 确保终端继承系统环境变量
   - `"path": "/bin/zsh"`: 指定 zsh 可执行文件路径

3. **验证配置**：
   - 重启 VSCode 使配置生效
   - 打开新终端，检查是否正确加载了 `.zshrc` 中的所有配置
   - 运行 `echo $PATH` 确认环境变量包含预期路径

**注意事项**：
- 如果使用的是 bash，将 `zsh` 替换为 `bash`，并确保使用 `-l` 参数
- 对于 Windows 系统，需要调整终端配置为适合 cmd 或 PowerShell 的参数

#### 3.2.5 虚拟环境配置说明

#### 为什么使用 `-m pytest` 方式运行测试

在 `launch.json` 中，我们使用以下方式运行 pytest：

```json
"program": "${workspaceFolder}/.venv/bin/python",
"args": [
    "-m",
    "pytest",
    "-xvs",
    "test/utils/test_bi_schema_extractor.py"
]
```

这种方式比直接调用 `pytest` 可执行文件（`${workspaceFolder}/.venv/bin/pytest`）更可靠，因为：

1. **确保使用正确的 Python 解释器**：直接指定虚拟环境中的 Python 解释器路径，避免使用系统默认的 Python 解释器
2. **环境变量正确加载**：虚拟环境的环境变量会被正确加载，包括依赖路径
3. **避免终端加载问题**：不需要依赖终端先激活虚拟环境，解决了终端未完全加载就执行测试的问题

#### 如何确保虚拟环境路径正确

1. 检查虚拟环境路径是否正确：`${workspaceFolder}/.venv/bin/python`
2. 确保虚拟环境已创建：如果没有虚拟环境，运行 `python -m venv .venv` 创建
3. 安装依赖：激活虚拟环境后运行 `pip install -r requirements-dev.txt` 安装测试依赖

#### 3.2.5 调试注意事项

1. **终端加载问题**：
   - 如果调试时遇到 "module not found" 错误，可能是虚拟环境未正确加载
   - 确保 `program` 字段指向虚拟环境中的 Python 解释器
   - 避免在终端中手动激活虚拟环境后再启动调试

2. **断点未触发**：
   - 检查 `justMyCode` 是否设置为 `false`，否则可能跳过第三方库代码
   - 确保断点设置在正确的行号

3. **调试速度慢**：
   - 可以暂时将 `justMyCode` 设置为 `true` 提高调试速度
   - 减少断点数量，只在关键位置设置断点

4. **环境变量问题**：
   - 如果测试需要环境变量，可以在 `launch.json` 中添加 `env` 字段
   - 例如：`"env": {"DEBUG": "1", "DB_NAME": "test_db"}`

4. **查看调用栈**
   - 在"调用栈"面板中可以查看函数调用的层级关系
   - 可以点击调用栈中的任意一层查看该层级的变量和代码

5. **使用调试控制台**
   - 在"调试控制台"面板中可以执行Python代码，查看和修改变量
   - 可以使用`print()`语句或直接输入变量名查看值

通过以上配置和方法，您可以在VSCode中方便地调试单元测试，快速定位和解决问题。

#### 3.2.4 VSCode调试配置说明

- **`program`**：指定pytest的路径，使用虚拟环境中的pytest确保依赖正确
- **`args`**：传递给pytest的参数
  - `-x`：遇到第一个失败就停止测试
  - `-v`：详细输出
  - `-s`：不捕获输出
- **`console`**：使用集成终端显示输出
- **`justMyCode`**：设置为`false`可以调试第三方库和测试框架代码
- **`workingDirectory`**：设置工作目录为项目根目录

这些配置确保了您可以在VSCode中高效地调试单元测试，提高开发和测试效率。

在单元测试中，测试内部方法（如 `get_table_schema_async`）是一种重要的策略，具有以下几个关键优势：

1. **全面覆盖**：内部方法可能包含复杂的业务逻辑、安全验证或数据处理，这些都需要单独验证
2. **问题定位**：当测试失败时，能更快定位到具体的问题所在
3. **代码质量**：直接测试内部方法可以确保其设计的合理性和健壮性
4. **重构支持**：内部方法的测试可以为代码重构提供安全保障

#### 3.2.2 单元测试分层策略

合理的单元测试应该采用分层策略：

1. **内部方法测试**：直接测试关键的内部方法，验证其核心逻辑
2. **公共接口测试**：测试对外暴露的公共方法，验证整体功能
3. **集成测试**：测试模块间的交互

#### 3.2.3 如何测试内部方法

对于 `get_table_schema_async` 这样的内部方法，我们可以：

1. **直接调用**：在测试中直接调用内部方法进行测试
2. **模拟依赖**：使用Mock替代其依赖的底层方法（如数据库查询）
3. **验证核心逻辑**：检查参数验证、SQL安全检查、结果格式化等关键环节

**示例：**
```python
@pytest.mark.asyncio
async def test_get_table_schema_async(self, metadata_extractor):
    """Test the internal get_table_schema_async method directly"""
    # Mock the database query
    mock_query_result = [
        {
            "Field": "id",
            "Type": "int(11)",
            "Key": "PRI",
            "Null": "NO",
            "Default": None,
            "Extra": "auto_increment",
            "Comment": "User ID"
        }
    ]
    
    with patch.object(metadata_extractor, '_execute_query_async') as mock_execute:
        mock_execute.return_value = mock_query_result
        
        # Call the internal method directly
        result = await metadata_extractor.get_table_schema_async(
            table_name="test_table",
            db_name="test_db"
        )
        
        # Verify the result
        assert len(result) == 1
        assert result[0]["column_name"] == "id"
        assert result[0]["data_type"] == "int(11)"
        assert result[0]["is_nullable"] is False
```

#### 3.2.4 平衡Mock使用与直接测试

- **适当使用Mock**：在测试高层方法时，Mock可以隔离依赖，使测试更可控
- **直接测试关键内部方法**：确保核心逻辑得到充分验证
- **避免过度Mock**：不要Mock所有依赖，否则测试可能失去意义

通过这种平衡的测试策略，可以确保测试既全面又高效，既能发现具体问题，又能验证整体功能。

### 3.4 Fixture

Fixture 是 pytest 中的一个概念，用于在测试用例执行前后进行一些准备和清理工作。

```python
@pytest.fixture
def metadata_extractor(self, mock_connection_manager):
    """创建 MetadataExtractor 实例"""
    return MetadataExtractor(
        db_name="test_db",
        catalog_name="internal",
        connection_manager=mock_connection_manager
    )
```

- 被 `@pytest.fixture` 装饰的函数会在测试用例执行前被调用
- Fixture 可以被其他测试用例或 Fixture 引用
- Fixture 用于创建测试环境和测试数据

### 3.5 断言（Assertion）

断言用于验证测试结果是否符合预期。

```python
assert result["success"] is True
assert "result" in result
assert result["result"] == mock_schema
```

- 如果断言失败，测试会被标记为失败
- 断言是验证代码行为的关键

### 3.6 异步测试

由于 `get_table_schema_for_mcp` 是一个异步方法，因此测试用例也需要使用异步方式编写。

```python
@pytest.mark.asyncio
async def test_get_table_schema_for_mcp_success(self, metadata_extractor):
    # 测试代码...
    result = await metadata_extractor.get_table_schema_for_mcp(...)
    # 断言...
```

- `@pytest.mark.asyncio`: 标记这是一个异步测试用例
- `async def`: 定义异步测试函数
- `await`: 调用异步方法

## 4. 测试用例覆盖范围

该测试文件覆盖了 `get_table_schema_for_mcp` 方法的多种场景：

| 测试用例 | 测试场景 |
|---------|---------|
| test_get_table_schema_for_mcp_success | 成功获取表结构 |
| test_get_table_schema_for_mcp_missing_table_name | 参数缺失 |
| test_get_table_schema_for_mcp_invalid_table_name | 无效表名 |
| test_get_table_schema_for_mcp_invalid_db_name | 无效数据库名 |
| test_get_table_schema_for_mcp_invalid_catalog_name | 无效目录名 |
| test_get_table_schema_for_mcp_table_not_found | 表不存在 |
| test_get_table_schema_for_mcp_exception | 异常处理 |
| test_get_table_schema_for_mcp_default_params | 默认参数 |
| test_get_table_schema_for_mcp_internal_catalog | 内部目录特殊处理 |

## 5. 运行测试

### 5.1 运行所有测试

```bash
cd /path/to/doris-mcp-server
python -m pytest test/utils/test_bi_schema_extractor.py -v
```

### 5.2 运行单个测试用例

```bash
python -m pytest test/utils/test_bi_schema_extractor.py::TestBiSchemaExtractor::test_get_table_schema_for_mcp_success -v
```

### 5.3 测试输出中的百分比进度

当您运行测试时，会看到类似以下的输出：

```
test/utils/test_bi_schema_extractor.py::TestBiSchemaExtractor::test_get_table_schema_for_mcp_success PASSED [ 11%]
test/utils/test_bi_schema_extractor.py::TestBiSchemaExtractor::test_get_table_schema_for_mcp_missing_table_name PASSED [ 22%]
```

**百分比的含义**：

输出中的百分比（如 `[ 11%]`、`[ 22%]`）表示**测试执行的进度**，即已完成的测试用例数占总测试用例数的百分比。

在 `test_bi_schema_extractor.py` 文件中，总共有9个测试用例：
- 第1个测试通过：`1/9 ≈ 11%`
- 第2个测试通过：`2/9 ≈ 22%`
- 以此类推，直到第9个测试通过：`9/9 = 100%`

这个进度指示器帮助您了解测试执行的当前状态，特别是当有多个测试用例时，可以直观地看到还有多少测试需要执行。

### 5.4 生成测试覆盖率报告

```bash
python -m pytest test/utils/test_bi_schema_extractor.py --cov=doris_mcp_server.utils.bi_schema_extractor -v
```

### 5.5 关于自动输出的测试覆盖率

当您运行测试时，可能会看到类似以下的覆盖率输出：

```
============================== tests coverage =============================== 
_____________ coverage: platform darwin, python 3.13.2-final-0 ______________
```

**为什么会自动输出测试覆盖率？**

这是因为项目的 `pyproject.toml` 文件中配置了自动收集和输出覆盖率信息。在 `[tool.pytest.ini_options]` 部分，有以下配置：

```toml
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=doris_mcp_server",    # 启用覆盖率收集
    "--cov-report=term-missing", # 在终端显示缺失的覆盖
    "--cov-report=html",         # 生成 HTML 覆盖率报告
    "--cov-report=xml",          # 生成 XML 覆盖率报告
]
```

同时，项目还安装了 `pytest-cov` 依赖（在 `requirements-dev.txt` 中），这是 pytest 的代码覆盖率插件。

**如何禁用自动输出的覆盖率信息？**

如果您不想看到覆盖率输出，可以使用 `--no-cov` 参数：

```bash
python -m pytest test/utils/test_bi_schema_extractor.py -v --no-cov
```

**覆盖率报告文件**

运行测试后，您会在项目根目录下找到以下覆盖率相关文件：
- `.coverage`: 覆盖率数据文件
- `coverage.xml`: XML 格式的覆盖率报告
- `htmlcov/`: HTML 格式的覆盖率报告目录（可在浏览器中打开查看详细覆盖率信息）

**覆盖率配置**

项目的覆盖率配置在 `pyproject.toml` 的 `[tool.coverage.run]` 和 `[tool.coverage.report]` 部分，您可以根据需要修改这些配置。

## 6. 测试设计原则

### 6.1 隔离性

单元测试应该相互独立，不依赖于外部资源（如数据库、网络等）。通过使用模拟对象，可以隔离被测试代码与外部依赖。

```python
# 使用模拟的连接管理器
mock_connection_manager = Mock()
metadata_extractor = MetadataExtractor(
    db_name="test_db",
    catalog_name="internal",
    connection_manager=mock_connection_manager
)
```

### 6.2 可重复性

单元测试应该是可重复的，无论运行多少次，结果都应该一致。通过使用模拟数据和固定的测试环境，可以确保测试的可重复性。

### 6.3 全面性

单元测试应该覆盖尽可能多的代码路径，包括正常情况和异常情况。该测试文件覆盖了成功、参数缺失、无效参数、异常处理等多种场景。

## 7. 总结

`test_bi_schema_extractor.py` 是一个使用 pytest 框架编写的单元测试文件，用于测试 `MetadataExtractor` 类的 `get_table_schema_for_mcp` 方法。通过使用模拟对象、Fixture、断言和异步测试等技术，确保了测试的隔离性、可重复性和全面性。

理解这些测试代码有助于更好地理解 `bi_schema_extractor.py` 中的 `get_table_schema_for_mcp` 方法的行为，以及如何编写高质量的 Python 单元测试。