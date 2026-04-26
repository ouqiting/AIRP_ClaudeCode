@echo off
chcp 65001 >nul
title DeepSeek Claude Code 一键配置
echo.
echo   正在启动配置脚本...
echo   如果弹出安全提示，请选择"是"或"允许"
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0setup-deepseek-claude.ps1"
pause
