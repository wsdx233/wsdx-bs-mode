#!/bin/bash
python -V
if [ $? -eq 0 ]; then
  echo 您已安装Python，将为您下载模组管理器
else
  echo 您未安装Python，正在为您安装Python
  apt-get update
  apt-get install python
fi

echo 正在为您安装必要的python库
pip install requests

echo 正在Mod管理器
wget -O bsmodins.py https://gitee.com/wsdx233/wsdx-bs-mode/raw/master/managers/bsmodins.py

echo 启动Mod管理器
python bsmodins.py