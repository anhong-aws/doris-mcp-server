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
BI Schema Extractor Unit Tests
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from doris_mcp_server.utils.bi_schema_extractor import MetadataExtractor
from doris_mcp_server.utils.sql_security_utils import SQLSecurityError


class TestBiSchemaExtractor:
    """BI Schema Extractor unit tests"""

    @pytest.fixture
    def mock_connection_manager(self):
        """Create mock connection manager"""
        return Mock()

    @pytest.fixture
    def metadata_extractor(self, mock_connection_manager):
        """Create metadata extractor instance"""
        return MetadataExtractor(
            db_name="test_db",
            catalog_name="internal",
            connection_manager=mock_connection_manager
        )

    @pytest.mark.asyncio
    async def test_get_table_schema_for_mcp_success(self, metadata_extractor):
        """Test successful table schema retrieval"""
        # Mock the get_table_schema_async method
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
        
        with patch.object(metadata_extractor, 'get_table_schema_async') as mock_get_schema:
            mock_get_schema.return_value = mock_schema
            
            # Call the method
            result = await metadata_extractor.get_table_schema_for_mcp(
                table_name="users",
                db_name="test_db",
                catalog_name="internal"
            )
            
            # Verify the result
            assert result["success"] is True
            assert "result" in result
            assert result["result"] == mock_schema
            mock_get_schema.assert_called_once_with(
                table_name="users",
                db_name="test_db",
                catalog_name="internal"
            )

    @pytest.mark.asyncio
    async def test_get_table_schema_for_mcp_missing_table_name(self, metadata_extractor):
        """Test missing table_name parameter"""
        # Call the method without table_name
        result = await metadata_extractor.get_table_schema_for_mcp(
            table_name="",
            db_name="test_db",
            catalog_name="internal"
        )
        
        # Verify the result
        assert result["success"] is False
        assert result["error"] == "Missing table_name parameter"

    @pytest.mark.asyncio
    async def test_get_table_schema_for_mcp_invalid_table_name(self, metadata_extractor):
        """Test invalid table name"""
        # Mock the validate_identifier function to raise an exception
        with patch('doris_mcp_server.utils.bi_schema_extractor.validate_identifier') as mock_validate:
            mock_validate.side_effect = SQLSecurityError("Invalid table name")
            
            # Call the method with invalid table name
            result = await metadata_extractor.get_table_schema_for_mcp(
                table_name="invalid-table-name",
                db_name="test_db",
                catalog_name="internal"
            )
            
            # Verify the result
            assert result["success"] is False
            assert "Invalid table name: invalid-table-name" in result["error"]
            assert "Table name contains invalid characters" in result["message"]

    @pytest.mark.asyncio
    async def test_get_table_schema_for_mcp_invalid_db_name(self, metadata_extractor):
        """Test invalid database name"""
        # Mock the validate_identifier function to raise an exception for db_name
        with patch('doris_mcp_server.utils.bi_schema_extractor.validate_identifier') as mock_validate:
            # First call for table name should succeed, second call for db name should fail
            def side_effect(identifier, name):
                if name == "database name":
                    raise SQLSecurityError("Invalid database name")
            mock_validate.side_effect = side_effect
            
            # Call the method with invalid db name
            result = await metadata_extractor.get_table_schema_for_mcp(
                table_name="users",
                db_name="invalid-db-name",
                catalog_name="internal"
            )
            
            # Verify the result
            assert result["success"] is False
            assert "Invalid database name: invalid-db-name" in result["error"]
            assert "Database name contains invalid characters" in result["message"]

    @pytest.mark.asyncio
    async def test_get_table_schema_for_mcp_invalid_catalog_name(self, metadata_extractor):
        """Test invalid catalog name"""
        # Mock the validate_identifier function to raise an exception for catalog_name
        with patch('doris_mcp_server.utils.bi_schema_extractor.validate_identifier') as mock_validate:
            # First two calls for table and db names should succeed, third call for catalog name should fail
            def side_effect(identifier, name):
                if name == "catalog name":
                    raise SQLSecurityError("Invalid catalog name")
            mock_validate.side_effect = side_effect
            
            # Call the method with invalid catalog name
            result = await metadata_extractor.get_table_schema_for_mcp(
                table_name="users",
                db_name="test_db",
                catalog_name="invalid-catalog-name"
            )
            
            # Verify the result
            assert result["success"] is False
            assert "Invalid catalog name: invalid-catalog-name" in result["error"]
            assert "Catalog name contains invalid characters" in result["message"]

    @pytest.mark.asyncio
    async def test_get_table_schema_for_mcp_table_not_found(self, metadata_extractor):
        """Test table not found scenario"""
        # Mock the get_table_schema_async method to return None
        with patch.object(metadata_extractor, 'get_table_schema_async') as mock_get_schema:
            mock_get_schema.return_value = None
            
            # Call the method
            result = await metadata_extractor.get_table_schema_for_mcp(
                table_name="non_existent_table",
                db_name="test_db",
                catalog_name="internal"
            )
            
            # Verify the result
            assert result["success"] is False
            assert "Table does not exist or has no columns" in result["error"]
            assert "non_existent_table" in result["message"]

    @pytest.mark.asyncio
    async def test_get_table_schema_for_mcp_exception(self, metadata_extractor):
        """Test exception handling"""
        # Mock the get_table_schema_async method to raise an exception
        with patch.object(metadata_extractor, 'get_table_schema_async') as mock_get_schema:
            mock_get_schema.side_effect = Exception("Database connection error")
            
            # Call the method
            result = await metadata_extractor.get_table_schema_for_mcp(
                table_name="users",
                db_name="test_db",
                catalog_name="internal"
            )
            
            # Verify the result
            assert result["success"] is False
            assert "Database connection error" in result["error"]
            assert "Error occurred while getting table schema" in result["message"]

    @pytest.mark.asyncio
    async def test_get_table_schema_for_mcp_default_params(self, metadata_extractor):
        """Test with default parameters"""
        # Mock the get_table_schema_async method with non-empty schema
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
            
            # Call the method with only table_name
            result = await metadata_extractor.get_table_schema_for_mcp(
                table_name="users"
            )
            
            # Verify the result
            assert result["success"] is True
            mock_get_schema.assert_called_once_with(
                table_name="users",
                db_name=None,
                catalog_name=None
            )

    @pytest.mark.asyncio
    async def test_get_table_schema_for_mcp_internal_catalog(self, metadata_extractor):
        """Test with internal catalog (should skip validation)"""
        # Mock the get_table_schema_async method with non-empty schema
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
            
            # Call the method with internal catalog
            result = await metadata_extractor.get_table_schema_for_mcp(
                table_name="users",
                db_name="test_db",
                catalog_name="internal"
            )
            
            # Verify the result
            assert result["success"] is True
            mock_get_schema.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_table_schema_async(self, metadata_extractor):
        """Test the internal get_table_schema_async method directly"""
        # Mock the _execute_query_with_catalog_async method with table schema data
        mock_query_result = [
            {
                "Field": "id",
                "Type": "int(11)",
                "Key": "PRI",
                "Null": "NO",
                "Default": None,
                "Extra": "auto_increment",
                "Comment": "User ID"
            },
            {
                "Field": "name",
                "Type": "varchar(255)",
                "Key": "",
                "Null": "YES",
                "Default": None,
                "Extra": "",
                "Comment": "User Name"
            }
        ]
        
        with patch.object(metadata_extractor, '_execute_query_with_catalog_async') as mock_execute:
            mock_execute.return_value = mock_query_result
            
            # Call the internal method directly
            result = await metadata_extractor.get_table_schema_async(
                table_name="test_table",
                db_name="test_db",
                catalog_name="test_catalog"
            )
            
            # Verify the result
            assert len(result) == 2
            assert result[0]["column_name"] == "id"
            assert result[0]["data_type"] == "int(11)"
            assert result[0]["is_nullable"] is False
            assert result[1]["column_name"] == "name"
            assert result[1]["data_type"] == "varchar(255)"
            assert result[1]["is_nullable"] is True
            
            # Verify the query was executed with correct parameters
            mock_execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_table_schema_async_with_catalog(self, metadata_extractor):
        """Test get_table_schema_async with catalog parameter"""
        # Mock the catalog-aware query method
        mock_query_result = [
            {
                "Field": "id",
                "Type": "int(11)",
                "Key": "PRI",
                "Null": "NO",
                "Default": None,
                "Extra": "",
                "Comment": "ID"
            }
        ]
        
        with patch.object(metadata_extractor, '_execute_query_with_catalog_async') as mock_catalog_query:
            mock_catalog_query.return_value = mock_query_result
            
            # Call with catalog parameter
            result = await metadata_extractor.get_table_schema_async(
                table_name="test_table",
                db_name="test_db",
                catalog_name="test_catalog"
            )
            
            # Verify results
            assert len(result) == 1
            assert result[0]["column_name"] == "id"
            
            # Only the catalog-aware method should be called (BUGFIX: Removed redundant _execute_query_async call)
            mock_catalog_query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_table_schema_async_invalid_identifier(self, metadata_extractor):
        """Test get_table_schema_async with invalid identifier"""
        # Test with table name containing SQL injection
        result = await metadata_extractor.get_table_schema_async(
            table_name="test_table; DROP TABLE users;",
            db_name="test_db"
        )
        
        # Should return empty list for invalid identifiers
        assert result == []

# Run tests with: pytest test_bi_schema_extractor.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])