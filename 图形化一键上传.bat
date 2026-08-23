@echo off
cd /d "%~dp0"
set PYTHON_EXE=C:\Users\QQ\AppData\Local\Programs\Python\Python313\pythonw.exe

if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

start "" "%PYTHON_EXE%" "%~dp0upload_gui.py"
exit
