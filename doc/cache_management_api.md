# Doris MCP Server 缓存管理 API

## 概述

Doris MCP Server 提供了完整的缓存管理系统，用于监控、管理和优化元数据缓存。本文档详细介绍了缓存管理API的使用方法、接口规范和最佳实践。

## 缓存系统架构

Doris MCP Server 的缓存系统主要包含以下组件：

- **元数据缓存**: 存储表结构、数据库表列表等元数据信息
- **缓存管理器**: 统一管理缓存的生命周期、性能监控和清理策略
- **HTTP API接口**: 提供RESTful接口用于缓存管理

## HTTP API 接口

### 基础URL
```
http://localhost:3000/cache/
```

### 认证说明
缓存管理接口需要适当的认证令牌。可以通过以下方式提供：
- Authorization header: `Bearer <token>`
- Token header: `Token <token>`
- Query parameter: `?token=<token>`

### 1. 获取缓存详情

**接口地址**: `GET /cache/details`

**功能描述**: 获取详细的缓存信息，包括缓存状态、键、值、大小、年龄等。

**请求参数**:
- `include_values` (可选): 是否包含缓存值，默认为 `false`
  - `true`: 包含缓存值的预览（10KB以内）
  - `false`: 不包含缓存值

**请求示例**:
```bash
# 获取缓存基本信息
curl "http://localhost:3000/cache/details"

# 包含缓存值预览
curl "http://localhost:3000/cache/details?include_values=true"
```

**响应示例**:
```json
{
  "success": true,
  "timestamp": "2026-01-05T10:30:00",
  "cache_summary": {
    "total_entries": 15,
    "cache_ttl_seconds": 3600,
    "cache_types": {
      "table_schema": 10,
      "database_tables": 2,
      "other": 3
    },
    "generated_at": "2026-01-05T10:30:00"
  },
  "cache_entries": [
    {
      "key": "table_schema:mydb:user_table",
      "age_seconds": 1800.5,
      "age_human": "0:30:00",
      "created_at": "2026-01-05T10:00:00",
      "is_expired": false,
      "cache_type": "table_schema",
      "value_size": 2048,
      "value_type": "list",
      "value_preview": "[{\"column_name\": \"id\", \"data_type\": \"int\"}, ...]"
    }
  ],
  "statistics": {
    "valid_entries": 12,
    "expired_entries": 3,
    "cache_efficiency": "80.0%",
    "oldest_entry_age": 3600.0,
    "newest_entry_age": 1800.0
  }
}
```

### 2. 获取缓存统计信息

**接口地址**: `GET /cache/statistics`

**功能描述**: 获取缓存系统的综合统计信息和性能指标。

**请求示例**:
```bash
curl "http://localhost:3000/cache/statistics"
```

**响应示例**:
```json
{
  "success": true,
  "statistics": {
    "valid_entries": 12,
    "expired_entries": 3,
    "cache_efficiency": "80.0%",
    "cache_performance": {
      "hit_potential": "80.0%",
      "memory_usage": {
        "total_size_bytes": 5242880,
        "total_size_human": "5.0 MB",
        "average_entry_size": 349525
      }
    },
    "cache_types": {
      "table_schema": {
        "count": 10,
        "valid_count": 8,
        "expired_count": 2,
        "total_size": 4194304
      },
      "database_tables": {
        "count": 2,
        "valid_count": 2,
        "expired_count": 0,
        "total_size": 1048576
      }
    },
    "recommendations": [
      "Cache performance looks good.",
      "Consider reducing cache TTL to free up memory."
    ]
  },
  "timestamp": "2026-01-05T10:30:00"
}
```

### 3. 清除缓存

**接口地址**: `GET /cache/clear` 或 `POST /cache/clear`

**功能描述**: 清除指定类型的缓存或特定缓存键。

**请求参数**:
- `cache_type` (可选): 要清除的缓存类型
  - `all`: 清除所有缓存
  - `table_schema`: 清除表结构缓存
  - `database_tables`: 清除数据库表缓存
  - `expired`: 清除过期缓存（默认）
- `specific_keys` (可选): 要清除的特定缓存键列表

**请求示例**:
```bash
# 清除所有缓存（GET方式）
curl "http://localhost:3000/cache/clear?cache_type=all"

# 清除过期缓存（GET方式，默认）
curl "http://localhost:3000/cache/clear?cache_type=expired"

# 清除特定缓存键（POST方式）
curl -X POST "http://localhost:3000/cache/clear" \
  -H "Content-Type: application/json" \
  -d '{
    "cache_type": "table_schema",
    "specific_keys": ["table_schema:mydb:user_table", "table_schema:mydb:order_table"]
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "Successfully cleared 5 cache entries",
  "cleared_entries": [
    "table_schema:mydb:user_table",
    "table_schema:mydb:order_table",
    "database_tables:mydb"
  ],
  "cleared_count": 5,
  "remaining_cache_size": 10,
  "operation": "clear_table_schema_cache",
  "timestamp": "2026-01-05T10:30:00"
}
```

### 4. 刷新缓存条目

**接口地址**: `GET /cache/refresh` 或 `POST /cache/refresh`

**功能描述**: 刷新特定的缓存条目，删除后将在下次请求时重新生成。

**请求参数**:
- `cache_key` (必需): 要刷新的缓存键

**请求示例**:
```bash
# 刷新特定缓存条目
curl "http://localhost:3000/cache/refresh?cache_key=table_schema:mydb:user_table"

# POST方式
curl -X POST "http://localhost:3000/cache/refresh" \
  -H "Content-Type: application/json" \
  -d '{"cache_key": "table_schema:mydb:user_table"}'
```

**响应示例**:
```json
{
  "success": true,
  "message": "Cache entry refreshed: table_schema:mydb:user_table",
  "key": "table_schema:mydb:user_table",
  "timestamp": "2026-01-05T10:30:00"
}
```

### 5. 搜索缓存键

**接口地址**: `GET /cache/search`

**功能描述**: 搜索匹配指定模式的缓存键。

**请求参数**:
- `pattern` (必需): 搜索模式（简单字符串匹配，不区分大小写）

**请求示例**:
```bash
# 搜索包含特定模式的缓存键
curl "http://localhost:3000/cache/search?pattern=table_schema"

# 搜索特定数据库的缓存
curl "http://localhost:3000/cache/search?pattern=mydb"
```

**响应示例**:
```json
{
  "success": true,
  "pattern": "table_schema",
  "matched_keys": [
    "table_schema:mydb:user_table",
    "table_schema:mydb:order_table",
    "table_schema:other_db:product_table"
  ],
  "match_count": 3,
  "timestamp": "2026-01-05T10:30:00"
}
```

## 缓存类型说明

### 1. 表结构缓存 (`table_schema`)
- **用途**: 缓存表的列信息、数据类型、约束等元数据
- **键格式**: `table_schema:<database>:<table>`
- **典型大小**: 1-5KB per table

### 2. 数据库表缓存 (`database_tables`)
- **用途**: 缓存数据库中的表列表信息
- **键格式**: `database_tables:<database>`
- **典型大小**: 100-500KB per database

## 缓存管理最佳实践

### 1. 监控缓存性能
```bash
# 定期检查缓存统计
curl "http://localhost:3000/cache/statistics" | jq '.statistics.cache_performance.hit_potential'
```

### 2. 清理策略
```bash
# 清理过期缓存（推荐定期执行）
curl -X POST "http://localhost:3000/cache/clear" \
  -H "Content-Type: application/json" \
  -d '{"cache_type": "expired"}'

# 清理特定类型的缓存（如果发现性能问题）
curl "http://localhost:3000/cache/clear?cache_type=table_schema"
```

### 3. 特定场景的缓存管理

#### 数据库结构变更后
```bash
# 清除所有相关缓存
curl -X POST "http://localhost:3000/cache/clear" \
  -H "Content-Type: application/json" \
  -d '{"cache_type": "table_schema"}'
```

#### 性能优化
```bash
# 搜索并刷新热点缓存
curl "http://localhost:3000/cache/search?pattern=table_schema:mydb" | jq '.matched_keys[]' | \
xargs -I {} curl "http://localhost:3000/cache/refresh?cache_key={}"
```

### 4. 自动化缓存管理脚本

```bash
#!/bin/bash
# 缓存健康检查脚本
BASE_URL="http://localhost:3000"

echo "=== 缓存健康检查 ==="

# 获取缓存统计
echo "1. 获取缓存统计..."
STATISTICS=$(curl -s "${BASE_URL}/cache/statistics")

# 检查缓存效率
EFFICIENCY=$(echo "$STATISTICS" | jq -r '.statistics.cache_performance.hit_potential')
echo "缓存效率: $EFFICIENCY"

# 检查过期条目比例
EXPIRED=$(echo "$STATISTICS" | jq -r '.statistics.expired_entries')
TOTAL=$(echo "$STATISTICS" | jq -r '.statistics.valid_entries + .statistics.expired_entries')
EXPIRED_RATIO=$(echo "scale=2; $EXPIRED * 100 / $TOTAL" | bc)

echo "过期条目比例: ${EXPIRED_RATIO}%"

# 如果过期比例超过50%，自动清理
if (( $(echo "$EXPIRED_RATIO > 50" | bc -l) )); then
    echo "过期缓存比例过高，自动清理..."
    curl -X POST "${BASE_URL}/cache/clear" \
      -H "Content-Type: application/json" \
      -d '{"cache_type": "expired"}'
    echo "清理完成"
fi

echo "=== 检查完成 ==="
```

## 错误处理

### 常见错误码

- **400 Bad Request**: 参数错误或缺少必需参数
- **401 Unauthorized**: 认证失败
- **500 Internal Server Error**: 服务器内部错误

### 错误响应示例
```json
{
  "success": false,
  "error": "Invalid cache type: invalid_type. Use 'all', 'table_schema', 'database_tables', or None for expired cache",
  "timestamp": "2026-01-05T10:30:00"
}
```

## 配置说明

### 缓存TTL配置
缓存的生存时间可以通过环境变量配置：
```bash
export METADATA_CACHE_TTL=7200  # 2小时，默认3600秒
```

### 重启服务器
修改缓存TTL后需要重启服务器使配置生效：
```bash
# 使用systemd
sudo systemctl restart doris-mcp-server

# 或直接重启
pkill -f doris-mcp-server
python -m doris_mcp_server.main --transport http --port 3000
```

## 监控和告警

### 关键指标
1. **缓存命中率**: `statistics.cache_performance.hit_potential`
2. **内存使用**: `statistics.cache_performance.memory_usage.total_size_bytes`
3. **过期比例**: `(expired_entries / total_entries) * 100`

### 告警建议
- 缓存命中率低于70%
- 内存使用超过50MB
- 过期缓存比例超过50%

## 故障排除

### 1. 缓存未更新
- 检查TTL设置是否过长
- 手动刷新相关缓存条目
- 检查数据库连接状态

### 2. 内存使用过高
- 清理过期缓存
- 减少TTL设置
- 检查缓存条目大小

### 3. API响应慢
- 检查缓存统计信息
- 清理大量缓存条目
- 优化查询模式

---

*本文档最后更新时间: 2026-01-05*