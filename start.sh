#!/bin/bash

# 启动服务端
echo "启动服务端..."
python server.py &
sleep 2

# 启动AI Agent
echo "启动AI Agent..."
python agents/alice.py &
sleep 1
python agents/bob.py &
sleep 1
python agents/charlie.py &
sleep 1
python agents/david.py &
sleep 1

# 启动用户客户端
echo "启动用户客户端..."
python user_client.py
