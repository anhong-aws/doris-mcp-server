# 配置管理功能实现计划

## 概述

本计划将实现一个完整的配置管理功能，分离配置的查看和编辑功能：
- **查看界面**：只能查看配置项，不能直接编辑
- **编辑界面**：单独的标签/界面，直接加载.env文件内容进行编辑、保存

## 实现步骤

### 1. 创建配置管理HTML模板

**文件**: `doris_mcp_server/templates/config_templates.py`

* 按照`cache_templates.py`的设计风格创建`CONFIG_MANAGEMENT_HTML`模板

* 实现标签页式界面，分离查看和编辑功能：

  * **查看配置**标签：

    * 基本配置

    * 数据库配置

    * 安全配置

    * 性能配置

    * 日志配置

    * 监控配置

    * ADBC配置

    * 数据质量配置

  * **编辑配置**标签：

    * 加载.env文件内容的文本编辑器（带语法高亮）

    * 显示当前.env文件路径

    * 保存和重置按钮

    * 备份提示

* 在查看配置界面中，所有配置项为只读显示

* 在编辑配置界面中，提供完整的.env文件编辑功能

* 添加配置验证功能

### 2. 创建配置管理处理器

**文件**: `doris_mcp_server/auth/config_handlers.py`

* 创建`ConfigHandlers`类，遵循现有处理器模式

* 实现以下方法：

  * `handle_config_management_page`: 提供HTML页面

  * `handle_get_config_details`: 获取当前配置详情（用于查看界面）

  * `handle_get_env_file`: 获取.env文件内容（用于编辑界面）

  * `handle_save_env_file`: 保存.env文件内容，创建备份，并重新加载配置

* 使用`BasicAuthHandlers`进行身份验证

* 实现配置验证

### 3. 更新首页模板，添加配置管理链接

**文件**: `doris_mcp_server/templates/index_templates.py`

* 在`INDEX_PAGE_DISABLED_HTML`的nav-links中添加配置管理链接

* 在`INDEX_PAGE_ENABLED_HTML`的nav-links中添加配置管理链接

* 使用合适的图标（`fas fa-cog`）

### 4. 在main.py中注册路由

**文件**: `doris_mcp_server/main.py`

* 添加`ConfigHandlers`的导入

* 创建`config_handlers`实例

* 添加路由定义：

  * `Route("/config/management", config_management, methods=["GET"])`

  * `Route("/config/details", config_details, methods=["GET"])`

  * `Route("/config/env-content", get_env_content, methods=["GET"])`

  * `Route("/config/save-env", save_env, methods=["POST"])`

* 在`mcp_app`函数的请求处理逻辑中添加`/config/`路径支持

### 5. 增强DorisConfig类

**文件**: `doris_mcp_server/utils/config.py`

* 添加`get_env_file_path`方法：获取当前使用的.env文件路径

* 添加`load_env_file_content`方法：读取.env文件内容

* 添加`save_to_env`方法：将配置保存到.env文件

* 实现带时间戳的.env文件备份功能

* 添加`reload_config`方法：重新加载配置

* 增强验证方法

## 技术细节

### 配置查看流程

1. 用户访问配置管理页面
2. 前端加载查看配置标签
3. 发送GET请求到`/config/details`获取当前配置
4. 后端返回结构化配置数据
5. 前端渲染只读配置界面

### 配置编辑流程

1. 用户切换到编辑配置标签
2. 前端发送GET请求到`/config/env-content`获取.env文件内容
3. 后端返回.env文件内容
4. 前端在编辑器中显示内容
5. 用户编辑内容
6. 用户点击保存按钮
7. 前端发送POST请求到`/config/save-env`，包含编辑后的内容
8. 后端执行：

   a. 创建.env文件备份（带时间戳）

   b. 保存新内容到.env文件

   c. 重新加载配置到内存

   d. 更新环境变量

9. 返回成功响应

### 安全考虑

* 所有端点都受`BasicAuthHandlers`保护

* 修改.env文件前创建备份

* 实现配置验证，确保保存的.env文件格式正确

* 编辑器提供语法高亮，减少编辑错误

## 预期变更

* 创建/修改4个文件

* 首页添加配置管理链接

* 完整的Web配置管理界面

* 分离的查看和编辑功能

* 直接编辑.env文件的功能

* 配置持久化和备份

* 配置重新加载

## 测试方法

1. Web界面手动测试
2. 验证查看配置界面是否只读
3. 验证编辑配置界面是否能正确加载.env文件
4. 测试.env文件编辑和保存功能
5. 验证备份功能
6. 验证配置重新加载
7. 测试身份验证保护
8. 测试配置验证功能

本实现将遵循现有代码库模式，与当前系统无缝集成。