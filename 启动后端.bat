@echo off
chcp 65001 >nul
title 汽车销量预测系统 - 后端启动器
echo ============================================
echo  汽车销量预测系统 后端启动器
echo  服务地址: http://127.0.0.1:8000
echo ============================================
cd /d "%~dp0car-sales-backend"

rem ---- 探测 Python 解释器（优先项目 venv，其次系统 PATH）----
set "PYEXE=python"
if exist "%~dp0car-sales-backend\.venv\Scripts\python.exe" set "PYEXE=%~dp0car-sales-backend\.venv\Scripts\python.exe"
if exist "%~dp0.venv\Scripts\python.exe" set "PYEXE=%~dp0.venv\Scripts\python.exe"

rem ---- 检查 8000 端口是否已在运行 ----
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul
if %errorlevel%==0 (
  echo 后端已在运行（端口 8000 已被占用），无需重复启动。
) else (
  echo 使用解释器: %PYEXE%
  echo 正在启动后端服务（最小化窗口）...
  start "" /min %PYEXE% main.py
  echo 后端启动中，3 秒后浏览器可访问 http://127.0.0.1:5174
)

timeout /t 6 >nul
exit
