#!/bin/bash
# 文件名：01_root_minimal.sh
# 用法：sudo ./01_root_minimal.sh

USERNAME=pyuser
# 1. 建用户（已存在则跳过）
id -u $USERNAME &>/dev/null || useradd -m -s /bin/bash $USERNAME

# 2. 只装 curl/git，其他不动
apt update -qq
apt install -y curl git
# apt install -y gcc make libc6-dev   # 最小编译链
# apt install -y libssl-dev zlib1g-dev libbz2-dev libsqlite3-dev libreadline-dev
apt install -y curl bzip2
echo "==== root 阶段完成 ===="