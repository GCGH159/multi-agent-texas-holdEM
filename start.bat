@echo off
chcp 65001 >nul

REM Start Server
echo Starting Server...
start /min .venv\Scripts\python.exe server.py
ping localhost -n 3 > nul

REM Start AI Agents
echo Starting AI Agents...
start /min .venv\Scripts\python.exe agents\alice.py
ping localhost -n 2 > nul
start /min .venv\Scripts\python.exe agents\bob.py
ping localhost -n 2 > nul
start /min .venv\Scripts\python.exe agents\charlie.py
ping localhost -n 2 > nul
start /min .venv\Scripts\python.exe agents\david.py
ping localhost -n 2 > nul
start /min .venv\Scripts\python.exe agents\eve.py
ping localhost -n 2 > nul

REM Start User Client
echo Starting User Client...
.venv\Scripts\python.exe user_client.py
