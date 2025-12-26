#!/bin/bash
# 文件名：02_pyuser_conda.sh
# 用法：su - pyuser
#       ./02_pyuser_conda.sh

set -e
# --------- 非 root 守卫 ---------
if [[ $EUID -eq 0 ]]; then
    echo "❌  请切换到普通用户（如 pyuser）再执行本脚本！"
    exit 1
fi

########## 1. 装 miniconda（已存在则跳过） ##########
if [[ ! -d $HOME/miniconda3 ]]; then
    echo "==== 首次安装 miniconda ===="
    wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-$(arch).sh -O /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p $HOME/miniconda3
    rm -f /tmp/miniconda.sh
fi

########## 2. 初始化 conda（幂等） ##########
grep -q "conda init" ~/.bashrc || {
    $HOME/miniconda3/bin/conda init bash
}
source ~/.bashrc

########## 3. 创建/更新 3.13 环境 ##########
echo "==== 创建/更新 Python 3.13 环境 ===="
########## 3. 静默接受 ToS（首次才需要） ##########
conda tos show >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "==== 首次接受 conda ToS ===="
    conda tos accept --override-channels \
        --channel https://repo.anaconda.com/pkgs/main \
        --channel https://repo.anaconda.com/pkgs/r
fi
conda create -n py313 python=3.13 -y
conda activate py313

########## 4. 项目处理（克隆/更新 + venv） ##########
REPO_URL=https://github.com/anhong-aws/doris-mcp-server.git
PROJ_DIR=$HOME/doris-mcp-server

# 代码已存在就更新，否则克隆
if [[ -d $PROJ_DIR/.git ]]; then
    cd "$PROJ_DIR" && git pull
else
    git clone "$REPO_URL" "$PROJ_DIR"
fi

cd "$PROJ_DIR"
# venv 存在即复用，否则新建
[[ -f .venv/bin/activate ]] || python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 2>/dev/null

########## 5. 验证 ##########
echo "==== 环境版本 ===="
python -V