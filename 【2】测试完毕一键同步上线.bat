@echo off
chcp 65001 >nul
title 🚀 OmniMedia 测试完毕一键同步上线

echo =======================================================
echo   🚀 OmniMedia 生产环境一键发布助手
echo =======================================================
echo.

set /p msg=请输入本次更新说明（直接回车默认: "feat: update"）: 
if "%msg%"=="" set msg=feat: update

cd /d "%~dp0"
echo 正在添加文件变更...
git add .

echo 正在提交变更: %msg%
git commit -m "%msg%"

echo 正在推送到云端仓库 (自动触发 Vercel 生产上线)...
git push origin main

echo.
echo =======================================================
echo   ✅ 上线指令已发出！Vercel 将在 30 秒内完成全球生产部署。
echo   * 线上正式地址: https://qq520.varud.asia/admin
echo =======================================================
echo.
pause