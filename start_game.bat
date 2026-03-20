@echo off

echo =======================================
echo 德州扑克多Agent游戏启动脚本
echo =======================================
echo 
echo 正在启动游戏...
echo 

REM 检查虚拟环境是否存在
if not exist ".venv\Scripts\python.exe" (
    echo 错误：虚拟环境不存在！
    echo 请先创建并激活虚拟环境，然后安装AgentScope
    pause
    exit /b 1
)

REM 运行游戏
.venv\Scripts\python main.py

REM 游戏结束后暂停，让用户查看结果
echo 
echo 游戏已结束，按任意键退出...
pause > nul
