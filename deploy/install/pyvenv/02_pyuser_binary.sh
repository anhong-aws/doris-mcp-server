#!/bin/bash
# 文件名：02_pyuser_binary.sh
# 用法：sudo -iu pyuser ./02_pyuser_binary.sh

# 拒绝 root 执行
if [[ $EUID -eq 0 ]]; then
   echo "❌  请切换到普通用户（如 pyuser）再执行本脚本，root 禁止运行！"
   exit 1
fi

set -e
########## 1. 装 pyenv（已存在则跳过） ##########
if [ ! -d "$HOME/.pyenv" ]; then
    curl -fsSL https://pyenv.run | bash
fi

########## 2. 写启动配置（幂等：只追加一次） ##########
grep -q "pyenv init" ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
EOF
source ~/.bashrc

########## 3. 二进制方式装 3.13.10（已装则跳过） ##########
pyenv versions | grep -q 3.13.2 || pyenv install 3.13.2:binary   # 秒下二进制
pyenv global 3.13.2

########## 4. 项目处理（同以前，幂等） ##########
REPO_URL=https://github.com/anhong-aws/doris-mcp-server.git
PROJ_DIR=$HOME/doris-mcp-server

# 克隆/更新
if [ -d "$PROJ_DIR/.git" ]; then
    cd "$PROJ_DIR" && git pull
else
    git clone "$REPO_URL" "$PROJ_DIR"
fi

cd "$PROJ_DIR"
# venv 存在即复用，否则新建
[ -f .venv/bin/activate ] || python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -U -r requirements.txt 2>/dev/null || pip install -U mcp pydantic uvicorn fastapi

########## 5. 验证 ##########
echo "==== 版本确认 ===="
python -V          # 应输出 3.13.10