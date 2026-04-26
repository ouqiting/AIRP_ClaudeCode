@echo off
chcp 65001 >nul
title DeepSeek + Claude Code Setup
echo.
echo   Launching setup script...
echo   If a security prompt appears, select "Yes" or "Allow"
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0setup-deepseek-claude.ps1"
pause
