#!/bin/bash

# 检查当前用户是否为 pyuser，如果不是则退出
CURRENT_USER=$(whoami)
if [ "$CURRENT_USER" != "pyuser" ]; then
    echo "错误: 此脚本需要以 pyuser 用户身份运行"
    echo "当前用户: $CURRENT_USER"
    echo "请使用: sudo -iu pyuser"
    exit 1
fi

echo "开始执行 Doris MCP Server 重新部署..."

# 查找占用 3000 端口的进程ID
echo "正在查找占用 3000 端口的进程..."
lsof -t -i:3000

# 强制终止占用 3000 端口的进程（如果存在），否则输出端口已清理的信息
echo "正在清理端口 3000..."
# kill $(lsof -t -i:3000 -nP -sTCP:LISTEN 2>/dev/null) 2>/dev/null || echo "3000 端口已干净"
pkill -f doris_mcp_server.main
echo "休眠一小段时间，再强制清理进程..."
sleep 25
pkill -9 -f doris_mcp_server.main

# 在后台启动服务器，将输出重定向到日志文件
echo "正在启动 Doris MCP Server..."
nohup ./start_server.sh >> logs/doris-mcp.out 2>&1 &
SERVER_PID=$!

# 等待服务器启动
echo "等待服务器启动..."
sleep 5

# 检查服务器是否成功启动
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "服务器启动成功，进程ID: $SERVER_PID"
    
    # 显示最近的启动日志
    echo "最近的启动日志:"
    tail -n 20 logs/doris-mcp.out
    
    # 等待服务器完全初始化
    echo "等待服务完全初始化..."
    sleep 3
    
    # 测试缓存管理API接口是否正常工作
    echo "测试缓存管理API接口..."
    if curl -s -f "http://localhost:3000/cache/details" > /dev/null; then
        echo "✓ 缓存管理API接口测试成功"
        curl "http://localhost:3000/cache/details" | head -n 10
    else
        echo "✗ 缓存管理API接口测试失败，请检查日志"
        echo "日志位置: logs/doris-mcp.out"
    fi
    
    echo ""
    echo "重新部署完成！服务器在后台运行，PID: $SERVER_PID"
    echo "查看日志: tail -f logs/doris-mcp.out"
    echo "停止服务器: kill $SERVER_PID"
else
    echo "✗ 服务器启动失败，请检查日志: logs/doris-mcp.out"
    exit 1
fi