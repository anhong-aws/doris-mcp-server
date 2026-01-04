#!/usr/bin/env python3
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
测试get_table_schema_for_mcp方法的集成测试
cd /Users/jarrywen/Downloads/aws/learn/ai/mcp/doris-mcp-server-6/doris-mcp-server && python -m pytest test/utils/test_get_table_schema_for_mcp.py -v -s
"""

import asyncio
import logging
from dotenv import load_dotenv

# 配置日志，确保输出到控制台
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

import pytest

from doris_mcp_server.utils.config import DorisConfig
from doris_mcp_server.utils.db import DorisConnectionManager
from doris_mcp_server.utils.bi_schema_extractor import MetadataExtractor

# 加载环境变量
load_dotenv()

# 获取日志记录器
logger = logging.getLogger(__name__)

async def test_direct_db_connection():
    """直接测试数据库连接，排除连接池管理问题"""
    # 从环境变量获取数据库配置
    from dotenv import load_dotenv
    load_dotenv()
    
    import os
    db_host = os.getenv("DORIS_HOST", "127.0.0.1")
    db_port = int(os.getenv("DORIS_PORT", "9030"))
    db_user = os.getenv("DORIS_USER", "root")
    db_password = os.getenv("DORIS_PASSWORD", "")
    db_name = os.getenv("DORIS_DATABASE", "")
    
    logger.info(f"尝试连接数据库: host={db_host}, port={db_port}, user={db_user}, db={db_name}")
    
    try:
        import aiomysql
        # 直接建立数据库连接
        connection = await aiomysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            db=db_name,
            charset="utf8mb4",
            connect_timeout=5
        )
        
        logger.info("成功连接到数据库")
        
        # 执行简单查询测试
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT 1")
            result = await cursor.fetchone()
            logger.info(f"简单查询结果: {result}")
            
            # 查询数据库中的表
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            table_names = [table[0] for table in tables]
            if len(table_names) > 3:
                logger.info(f"数据库中的表 (前3个): {table_names[:3]}... 共{len(table_names)}个表")
            else:
                logger.info(f"数据库中的表: {table_names}")
        
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        return False

class TestGetTableSchemaForMcp:
    """测试get_table_schema_for_mcp方法的集成测试类"""
    
    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """设置和清理测试环境"""
        # 先测试直接数据库连接
        logger.info("=== 测试直接数据库连接 ===")
        if not await test_direct_db_connection():
            pytest.skip("直接数据库连接失败，跳过测试")
        
        # 创建配置对象
        self.config = DorisConfig.from_env()
        
        # 初始化连接管理器
        self.connection_manager = DorisConnectionManager(self.config)
        
        # Initialize connection for stdio mode (as done in main.py)
        await self.connection_manager.initialize_for_stdio_mode()
        
        # 初始化MetadataExtractor
        self.metadata_extractor = MetadataExtractor(connection_manager=self.connection_manager)
        
        yield
        
        # 清理资源
        await self.connection_manager.close()
    
    @pytest.mark.asyncio
    async def test_existing_table_schema(self):
        """测试1: 获取存在的表的结构"""
        logger.info("\n=== 测试1: 获取存在的表的结构 ===")
        
        # 使用用户指定的表名
        table_name = "ads_energy_consume_mon"
        logger.info(f"使用表: {table_name} 进行测试")
        
        try:
            # 设置超时
            result = await asyncio.wait_for(
                self.metadata_extractor.get_table_schema_for_mcp(table_name),
                timeout=30.0
            )
            # 只显示两三个列名示例
            if result.get("success", False) and "result" in result and isinstance(result["result"], list):
                columns = result["result"]
                if len(columns) > 3:
                    sample_columns = columns[:3]
                    logger.info(f"表 {table_name} 的结构 (前3个列): {sample_columns}... 共{len(columns)}个列")
                else:
                    logger.info(f"表 {table_name} 的结构: {columns}")
            else:
                logger.info(f"表 {table_name} 的查询结果: {result}")
            assert result is not None
            assert isinstance(result, dict)
            
            # 检查响应格式
            if result.get("success", False):
                assert "result" in result
                assert isinstance(result["result"], list)
                logger.info("测试1成功")
            else:
                logger.warning(f"测试1: 表 {table_name} 可能不存在或没有列")
                logger.warning(f"错误信息: {result.get('error', '未知错误')}")
                logger.warning(f"详细信息: {result.get('message', '')}")
                # 如果表不存在，这个测试不应该失败，因为可能是环境问题
                pytest.skip(f"表 {table_name} 不存在或没有列")
        except asyncio.TimeoutError:
            logger.error(f"测试1超时")
            pytest.fail(f"测试1超时")
        except Exception as e:
            logger.error(f"测试1失败: {e}", exc_info=True)
            pytest.fail(f"测试1失败: {e}")
    
    @pytest.mark.asyncio
    async def test_nonexistent_table(self):
        """测试2: 获取不存在的表的结构"""
        logger.info("\n=== 测试2: 获取不存在的表的结构 ===")
        
        try:
            table_name = "non_existent_table_123456789"
            result = await asyncio.wait_for(
                self.metadata_extractor.get_table_schema_for_mcp(table_name),
                timeout=30.0
            )
            logger.info(f"表 {table_name} 的查询结果: {result}")
            
            # 根据源码，当表不存在时，应该返回success=False的响应，而不是抛出异常
            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success", False) is False
            assert "Table does not exist" in result.get("error", "") or "has no columns" in result.get("error", "")
            logger.info("测试2成功")
        except asyncio.TimeoutError:
            logger.error(f"测试2超时")
            pytest.fail(f"测试2超时")
        except Exception as e:
            logger.error(f"测试2失败: {e}", exc_info=True)
            pytest.fail(f"测试2失败: {e}")
    
    @pytest.mark.asyncio
    async def test_table_schema_with_db_name(self):
        """测试3: 指定数据库名获取表结构"""
        logger.info("\n=== 测试3: 指定数据库名获取表结构 ===")
        
        try:
            # 使用用户指定的表名和配置中的数据库名
            table_name = "ads_energy_consume_mon"
            db_name = self.config.database.database  # 使用配置中的数据库名
            result = await asyncio.wait_for(
                self.metadata_extractor.get_table_schema_for_mcp(table_name, db_name),
                timeout=30.0
            )
            # 只显示两三个列名示例
            if result.get("success", False) and "result" in result and isinstance(result["result"], list):
                columns = result["result"]
                if len(columns) > 3:
                    sample_columns = columns[:3]
                    logger.info(f"数据库 {db_name} 中的表 {table_name} 的结构 (前3个列): {sample_columns}... 共{len(columns)}个列")
                else:
                    logger.info(f"数据库 {db_name} 中的表 {table_name} 的结构: {columns}")
            else:
                logger.info(f"数据库 {db_name} 中的表 {table_name} 的查询结果: {result}")
            assert result is not None
            assert isinstance(result, dict)
            
            # 检查响应格式
            if result.get("success", False):
                assert "result" in result
                assert isinstance(result["result"], list)
                logger.info("测试3成功")
            else:
                logger.warning(f"测试3: 表 {table_name} 可能不存在或没有列")
                logger.warning(f"错误信息: {result.get('error', '未知错误')}")
                logger.warning(f"详细信息: {result.get('message', '')}")
                # 如果表不存在，这个测试不应该失败，因为可能是环境问题
                pytest.skip(f"表 {table_name} 不存在或没有列")
        except asyncio.TimeoutError:
            logger.error(f"测试3超时")
            pytest.fail(f"测试3超时")
        except Exception as e:
            logger.error(f"测试3失败: {e}", exc_info=True)
            pytest.fail(f"测试3失败: {e}")