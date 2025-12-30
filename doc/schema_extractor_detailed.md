# Schema Extractor 详细说明文档

## 1. 概述

`schema_extractor.py` 是 Apache Doris MCP Server 中的核心组件，负责从数据库中提取元数据信息，包括数据库、表、列、索引、表关系等。该组件提供了丰富的 API 接口，用于获取和管理数据库元数据，并实现了缓存机制以提高性能。

## 2. 全局变量

### 2.1 METADATA_DB_NAME

```python
METADATA_DB_NAME = "information_schema"
```

- **作用**：定义元数据数据库的名称，固定为 `information_schema`
- **使用位置**：在 `__init__` 方法中被赋值给 `self.metadata_db`
- **说明**：`information_schema` 是 Doris 数据库中的系统数据库，包含了所有数据库对象的元数据信息

### 2.2 ENABLE_MULTI_DATABASE

```python
ENABLE_MULTI_DATABASE = os.getenv("ENABLE_MULTI_DATABASE", True)
```

- **作用**：控制是否启用多数据库支持
- **默认值**：`True`（如果环境变量未设置）
- **配置方式**：通过环境变量 `ENABLE_MULTI_DATABASE` 设置
- **使用位置**：在 `__init__` 方法中被赋值给 `self.enable_multi_database`
- **说明**：当启用时，可以访问多个数据库的元数据信息

### 2.3 MULTI_DATABASE_NAMES

```python
MULTI_DATABASE_NAMES = os.getenv("MULTI_DATABASE_NAMES", "")
```

- **作用**：指定允许访问的数据库列表（以逗号分隔）
- **默认值**：空字符串（允许访问所有数据库）
- **配置方式**：通过环境变量 `MULTI_DATABASE_NAMES` 设置

## 3. 缓存系统

### 3.1 缓存结构

```python
self.metadata_cache = {}
self.metadata_cache_time = {}
self.cache_ttl = int(os.getenv("METADATA_CACHE_TTL", "3600"))
```

- **`metadata_cache`**：存储实际的缓存数据，键为缓存键，值为缓存的元数据
- **`metadata_cache_time`**：存储每个缓存条目的时间戳，用于检查缓存是否过期
- **`cache_ttl`**：缓存过期时间（秒），默认3600秒（1小时），可通过环境变量 `METADATA_CACHE_TTL` 配置

### 3.2 缓存键格式

缓存键的格式通常为：`{resource_type}_{effective_catalog or 'default'}_{db_name}_{table_name}`

示例：
- 数据库列表：`databases_default` 或 `databases_catalog_name`
- 表列表：`tables_default_dbname` 或 `tables_catalog_name_dbname`
- 表结构：`schema_default_dbname_tablename` 或 `schema_catalog_name_dbname_tablename`

### 3.3 缓存使用流程

1. **检查缓存**：在获取元数据之前，先检查缓存中是否存在对应的条目
2. **验证缓存过期**：通过比较当前时间与缓存时间戳，判断缓存是否过期
3. **使用缓存或查询**：如果缓存有效则直接返回，否则执行数据库查询
4. **更新缓存**：查询完成后，将结果存入缓存并更新时间戳

示例代码：

```python
def get_all_databases(self, catalog_name: str = None) -> List[str]:
    effective_catalog = catalog_name or self.catalog_name
    cache_key = f"databases_{effective_catalog or 'default'}"
    
    # 检查缓存是否有效
    if cache_key in self.metadata_cache and (datetime.now() - self.metadata_cache_time.get(cache_key, datetime.min)).total_seconds() < self.cache_ttl:
        return self.metadata_cache[cache_key]
    
    # 执行查询
    try:
        query = """
        SELECT SCHEMA_NAME 
        FROM information_schema.schemata 
        WHERE SCHEMA_NAME NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
        ORDER BY SCHEMA_NAME
        """
        result = self._execute_query_with_catalog(query, self.db_name, effective_catalog)
        databases = [db["SCHEMA_NAME"] for db in result] if result else []
        
        # 更新缓存
        self.metadata_cache[cache_key] = databases
        self.metadata_cache_time[cache_key] = datetime.now()
        
        return databases
    except Exception as e:
        logger.error(f"Error getting database list: {str(e)}")
        return []
```

### 3.4 缓存的优点

1. **提高性能**：减少数据库查询次数，提高响应速度
2. **降低数据库负载**：减少对 `information_schema` 的访问压力
3. **支持并发访问**：多线程环境下可以共享缓存数据

## 4. Session ID

### 4.1 定义与生成

```python
self._session_id = f"metadata_extractor_{uuid.uuid4().hex[:8]}"
```

- **作用**：为数据库查询提供唯一的会话标识符
- **生成方式**：使用 UUID 生成，格式为 `metadata_extractor_{8位UUID后缀}`
- **特点**：每个 `MetadataExtractor` 实例都有独立的会话ID

### 4.2 使用位置

Session ID 主要用于 `_execute_query_async` 方法中：

```python
async def _execute_query_async(self, query: str, db_name: str = None, return_dataframe: bool = False):
    # ...
    result = await self.connection_manager.execute_query(self._session_id, query, None)
    # ...
```

### 4.3 作用

1. **会话标识**：在 DorisConnectionManager 中标识不同的查询会话
2. **调试与追踪**：便于在日志中追踪特定会话的查询操作
3. **资源隔离**：不同的会话ID可以用于隔离查询资源

## 5. 核心方法

### 5.1 get_table_schema_async

```python
async def get_table_schema_async(self, table_name: str, db_name: str = None, catalog_name: str = None) -> List[Dict[str, Any]]:
    # ...
```

- **作用**：异步获取表的结构信息
- **参数**：
  - `table_name`：表名
  - `db_name`：数据库名（可选，默认使用实例的 `db_name`）
  - `catalog_name`：目录名（可选，默认使用实例的 `catalog_name`）
- **返回值**：包含表列信息的字典列表
- **缓存使用**：使用缓存键 `schema_{effective_catalog}_{db_name}_{table_name}` 缓存结果

### 5.2 get_database_tables_async

```python
async def get_database_tables_async(self, db_name: str = None, catalog_name: str = None) -> List[str]:
    # ...
```

- **作用**：异步获取数据库中的所有表名
- **参数**：
  - `db_name`：数据库名（可选，默认使用实例的 `db_name`）
  - `catalog_name`：目录名（可选，默认使用实例的 `catalog_name`）
- **返回值**：表名列表
- **缓存使用**：使用缓存键 `tables_{effective_catalog}_{db_name}` 缓存结果

### 5.3 _execute_query_with_catalog_async

```python
async def _execute_query_with_catalog_async(self, query: str, db_name: str = None, catalog_name: str = None):
    # ...
```

- **作用**：异步执行带目录的查询
- **参数**：
  - `query`：SQL查询语句
  - `db_name`：数据库名（可选）
  - `catalog_name`：目录名（可选）
- **说明**：当指定了目录名且查询涉及 `information_schema` 时，会重写查询语句以包含目录名，例如将 `information_schema.tables` 重写为 `{catalog_name}.information_schema.tables`

### 5.4 _execute_query_async

```python
async def _execute_query_async(self, query: str, db_name: str = None, return_dataframe: bool = False):
    # ...
```

- **作用**：异步执行基础查询
- **参数**：
  - `query`：SQL查询语句
  - `db_name`：数据库名（可选）
  - `return_dataframe`：是否返回DataFrame格式（默认False）
- **说明**：直接执行SQL查询，不进行目录重写，适用于普通查询和SHOW系列命令

### 5.5 查询执行方法的区别与使用场景

| 方法名称 | 目录支持 | 查询重写 | 适用场景 |
|---------|---------|---------|----------|
| `_execute_query_async` | ❌ | ❌ | 1. 执行SHOW命令（SHOW DATABASES, SHOW TABLES, SHOW CATALOGS）<br>2. 执行DESCRIBE查询<br>3. 不涉及information_schema的普通业务查询 |
| `_execute_query_with_catalog_async` | ✅ | ✅ | 1. 查询information_schema时需要指定目录<br>2. 跨目录查询元数据<br>3. 需要目录级别的元数据隔离 |

#### 使用information_schema的查询场景

在`schema_extractor.py`中，直接使用`_execute_query_async`查询`information_schema`的情况较少，主要出现在同步方法中。大部分异步查询`information_schema`的方法会使用`_execute_query_with_catalog_async`，以支持多目录场景。

**使用`_execute_query_async`查询information_schema的方法**：
- `get_table_schema`（同步方法）：使用该方法执行information_schema.tables查询获取表的类型和引擎信息

**使用`_execute_query_with_catalog_async`查询information_schema的方法**：
- `get_table_comment_async`：获取表注释
- `get_column_comments_async`：获取列注释

**使用`_execute_query_async`执行的其他查询**：
- SHOW DATABASES
- SHOW TABLES
- SHOW CATALOGS
- DESCRIBE {table}

## 6. 配置参数

| 环境变量 | 类型 | 默认值 | 描述 |
|---------|------|-------|------|
| METADATA_CACHE_TTL | 整数 | 3600 | 元数据缓存过期时间（秒） |
| ENABLE_MULTI_DATABASE | 布尔值 | True | 是否启用多数据库支持 |
| MULTI_DATABASE_NAMES | 字符串 | "" | 允许访问的数据库列表（逗号分隔） |
| ENABLE_TABLE_HIERARCHY | 布尔值 | False | 是否启用表层次结构排序 |
| TABLE_HIERARCHY_PATTERNS | JSON数组 | '["^ads_.*$","^dim_.*$","^dws_.*$","^dwd_.*$","^ods_.*$","^tmp_.*$","^stg_.*$","^.*$"]' | 表层次结构匹配模式 |
| EXCLUDED_DATABASES | JSON数组 | '["information_schema", "mysql", "performance_schema", "sys", "doris_metadata"]' | 排除的系统数据库列表 |

## 7. 类结构

### 7.1 MetadataExtractor

主类，提供元数据提取功能：

- **初始化参数**：
  - `db_name`：默认数据库名
  - `catalog_name`：默认目录名
  - `connection_manager`：数据库连接管理器实例

- **主要属性**：
  - `db_name`：当前数据库名
  - `catalog_name`：当前目录名
  - `metadata_cache`：元数据缓存
  - `cache_ttl`：缓存过期时间
  - `enable_multi_database`：是否启用多数据库支持
  - `_session_id`：会话ID

- **主要方法**：
  - `get_all_databases`：获取所有数据库名
  - `get_database_tables`：获取数据库中的所有表名
  - `get_table_schema`：获取表结构
  - `get_table_comment`：获取表注释
  - `get_column_comments`：获取列注释
  - `get_table_indexes`：获取表索引
  - `get_table_relationships`：获取表关系

### 7.2 MetadataManager

封装类，提供更简洁的 API 接口：

- **初始化参数**：
  - `connection_manager`：数据库连接管理器实例

- **主要方法**：
  - `exec_query`：执行查询
  - `get_table_schema`：获取表结构
  - `get_db_table_list`：获取数据库表列表
  - `get_db_list`：获取数据库列表
  - `get_table_comment`：获取表注释
  - `get_table_column_comments`：获取列注释
  - `get_table_indexes`：获取表索引

## 8. 最佳实践

### 8.1 缓存配置

1. **根据实际情况调整缓存时间**：
   - 如果元数据更新频繁，可缩短 `METADATA_CACHE_TTL`
   - 如果元数据更新较少，可延长 `METADATA_CACHE_TTL` 以提高性能

2. **监控缓存命中率**：
   - 可以添加日志记录缓存命中情况
   - 根据命中率调整缓存策略

### 8.2 多数据库支持

1. **合理配置 `MULTI_DATABASE_NAMES`**：
   - 只允许访问必要的数据库
   - 避免使用空字符串（允许访问所有数据库）

2. **注意权限控制**：
   - 确保数据库用户有足够的权限访问指定的数据库

### 8.3 性能优化

1. **使用异步方法**：
   - 优先使用带有 `_async` 后缀的异步方法
   - 异步方法可以提高并发性能

2. **批量获取元数据**：
   - 尽量批量获取元数据，减少网络请求次数

3. **使用缓存**：
   - 对于频繁访问的元数据，利用缓存提高响应速度

## 9. 总结

`schema_extractor.py` 是一个功能强大的元数据提取组件，通过缓存机制、会话管理和丰富的API接口，为 Doris MCP Server 提供了高效的元数据访问能力。理解其内部结构和工作原理，可以更好地使用和扩展该组件。

主要特点：

1. **高效的缓存系统**：减少数据库查询，提高性能
2. **灵活的配置选项**：支持多数据库、表层次结构等特性
3. **丰富的API接口**：提供同步和异步方法，满足不同场景需求
4. **安全的设计**：包含SQL注入防护、标识符验证等安全措施
5. **良好的可扩展性**：模块化设计，便于扩展和维护