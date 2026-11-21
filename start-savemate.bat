@echo off
REM SaveMate - Start Claude Code in project directory
REM This batch file switches to the project directory and launches Claude Code locally.

cd /d "D:\dev\savemate"

echo ==========================================
echo   SaveMate Development Environment
echo ==========================================
echo Project directory: D:\dev\savemate
echo Python: %LOCALAPPDATA%\Programs\Python\Python312\python.exe
echo pip: python -m pip
echo.
echo Starting Claude Code...
echo.

claude