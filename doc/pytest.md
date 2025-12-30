以下是一些常用的pytest命令示例：

运行所有测试：

Bash



运行
.venv/bin/pytest -xvs
运行特定文件的测试：

Bash



运行
.venv/bin/pytest test/utils/test_bi_schema_extractor.py -xvs
运行特定类的测试：

Bash



运行
.venv/bin/pytest test/utils/test_bi_schema_extractor.py::TestBiSchemaExtractor -xvs
运行特定函数的测试：

Bash



运行
.venv/bin/pytest test/utils/test_bi_schema_extractor.py::TestBiSchemaExtractor::test_get_table_schema_async -xvs
运行包含特定关键词的测试：

Bash



运行
.venv/bin/pytest -xvs -k "test_get_table_schema"
生成测试覆盖率报告：

Bash



运行
.venv/bin/pytest --cov=doris_mcp_server test/utils/test_bi_schema_extractor.py -xvs
生成HTML格式的覆盖率报告：

Bash



运行
.venv/bin/pytest --cov=doris_mcp_server --cov-report=html test/utils/test_bi_schema_extractor.py -xvs
常用选项说明：

-x：遇到测试失败立即停止
-v：详细输出
-s：显示print语句的输出
-k：根据关键词过滤测试
--cov：生成测试覆盖率报告
--cov-report：指定覆盖率报告的格式
如果您需要执行其他特定的测试或有任何其他问题，请告诉我。


如果您不想测量整个 doris_mcp_server 目录的覆盖率，可以指定更具体的子模块或文件。--cov 参数支持以下几种指定方式：

1. 指定单个子模块
Bash



运行
# 只测量 utils 子模块的覆盖率
.venv/bin/pytest --cov=doris_mcp_server.utils test/utils/test_bi_schema_extractor.py -xvs# 只测量 tools 子模块的覆盖率  .venv/bin/pytest --cov=doris_mcp_server.tools test/utils/test_bi_schema_extractor.py -xvs
2. 指定单个具体文件
Bash



运行
# 只测量 bi_schema_extractor.py 文件的覆盖率
.venv/bin/pytest --cov=doris_mcp_server.utils.bi_schema_extractor test/utils/test_bi_schema_extractor.py -xvs
3. 排除特定目录或文件
您还可以结合 --cov-exclude 参数排除不需要测量的部分：

Bash



运行
# 测量整个 doris_mcp_server，但排除 auth 模块
.venv/bin/pytest --cov=doris_mcp_server --cov-exclude="*/auth/*" test/utils/test_bi_schema_extractor.py -xvs
4. 同时测量多个模块
Bash



运行
# 同时测量 utils 和 tools 两个子模块
.venv/bin/pytest --cov=doris_mcp_server.utils --cov=doris_mcp_server.tools test/utils/test_bi_schema_extractor.py -xvs

注意：在pyproject.toml文件中有全局的pytest和coverage配置，这些配置覆盖了我们在命令行中指定的--cov参数。
--no-cov：禁用覆盖率测量，即使在pyproject.toml中配置了--cov参数也会被忽略。