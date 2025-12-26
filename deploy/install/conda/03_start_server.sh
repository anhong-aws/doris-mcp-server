cd doris-mcp-server/
source .venv/bin/activate
#./start_server.sh
nohup ./start_server.sh >> logs/doris-mcp.out 2>&1 &
