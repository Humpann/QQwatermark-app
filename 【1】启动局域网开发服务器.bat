@echo off
chcp 65001 >nul
title 🚀 OmniMedia 本地局域网开发测试服务器 (热重载模式)

echo =======================================================
echo   🚀 OmniMedia 局域网本地开发服务器启动中...
echo =======================================================
echo   * 本地后台地址: http://localhost:8888/admin
echo   * 局域网手机端: http://192.168.1.11:8888/admin
echo   * 当前模式: 【本地隔离开发】(任何修改均不影响线上)
echo =======================================================
echo.

cd /d "%~dp0"
"C:\Users\QQ\AppData\Local\Programs\Python\Python313\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload

pause