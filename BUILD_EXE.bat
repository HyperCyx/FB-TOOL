@echo off
REM FB Recovery Bot - Windows EXE Builder
REM This script builds a standalone Windows executable

echo.
echo ========================================================
echo   FB RECOVERY BOT - EXE BUILDER
echo   Building Windows Executable...
echo ========================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python found: 
python --version
echo.

REM Check if main file exists
if not exist "FB_Recovery_Bot_Complete.py" (
    echo [ERROR] FB_Recovery_Bot_Complete.py not found!
    echo Please run this script from the project directory.
    pause
    exit /b 1
)

REM Run the builder script
echo [INFO] Starting build process...
echo.
python build_exe.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo Check the error messages above for details.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   BUILD COMPLETE!
echo ========================================================
echo.
echo Your executable is ready:
echo   - EXE File: dist\FB_Recovery_Bot.exe
echo   - Distribution Package: FB_Recovery_Bot_Windows\
echo   - ZIP Archive: FB_Recovery_Bot_Windows_v1.0.zip
echo.
echo You can now share the ZIP file or the folder!
echo.
pause
