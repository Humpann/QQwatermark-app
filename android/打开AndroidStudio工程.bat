@echo off
chcp 65001 >nul
echo 正在打开 Android Studio 并导入 OmniMediaWatermarkApp 工程...
start "" "C:\Program Files\Android\Android Studio\bin\studio64.exe" "%~dp0."
exit
