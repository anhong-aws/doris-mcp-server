# 本机单独启动
export DORIS_HOST=36.212.156.218
export DORIS_PORT=9030
export DORIS_USER=root
export DORIS_PASSWORD=MyDoris202511
export DORIS_DATABASE=dw_power

export LOG_LEVEL=DEBUG
# stdio
uvx --from doris-mcp-server doris-mcp-server --transport stdio 2>&1 | tee mcp_debug_stdio.log
# http
uvx --from doris-mcp-server doris-mcp-server --transport http --host 127.0.0.1 --port 3000 2>&1 | tee mcp_debug_http.log