kill -9 $(lsof -t -i:3000 -nP -sTCP:LISTEN 2>/dev/null) 2>/dev/null || echo "3000 端口已干净"
kill -9 $(ps -ef | awk '/start_server\.sh/ && !/awk/ {print $2}')

cd doris-mcp-server/
source .venv/bin/activate
#./start_server.sh
nohup ./start_server.sh >> logs/doris-mcp.out 2>&1 &
