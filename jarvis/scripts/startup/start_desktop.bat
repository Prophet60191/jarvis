@echo off
REM Jarvis Desktop App Launcher Script for Windows
REM 
REM This script provides an easy way to launch the Jarvis Desktop Application
REM with different panels and configurations.
REM
REM Usage:
REM   start_desktop.bat                    # Main dashboard
REM   start_desktop.bat settings          # Settings panel
REM   start_desktop.bat audio             # Audio configuration

setlocal enabledelayedexpansion

REM Default values
set "PANEL=%~1"
set "PORT=8080"
set "DEBUG_FLAG="

REM Set default panel if not provided
if "%PANEL%"=="" set "PANEL=main"

REM Parse additional arguments
:parse_args
if "%~2"=="" goto :start_app
if "%~2"=="--port" (
    set "PORT=%~3"
    shift
    shift
    goto :parse_args
)
if "%~2"=="--debug" (
    set "DEBUG_FLAG=--debug"
    shift
    goto :parse_args
)
if "%~2"=="--help" goto :show_help
if "%~2"=="-h" goto :show_help
shift
goto :parse_args

:show_help
echo Jarvis Desktop App Launcher
echo.
echo Usage: %~nx0 [panel] [options]
echo.
echo Panels:
echo   main          Main dashboard (default)
echo   settings      Settings overview
echo   audio         Audio configuration
echo   llm           LLM settings
echo   conversation  Conversation settings
echo   logging       Logging configuration
echo   general       General settings
echo   voice-profiles Voice profile management
echo   device        Device information
echo.
echo Options:
echo   --port PORT   Custom port (default: 8080)
echo   --debug       Enable debug mode
echo   --help        Show this help
echo.
echo Examples:
echo   %~nx0                        # Main dashboard
echo   %~nx0 settings              # Settings panel
echo   %~nx0 audio --port 3000     # Audio config on port 3000
echo   %~nx0 llm --debug           # LLM settings with debug
exit /b 0

:start_app
REM Validate panel
set "VALID=0"
for %%p in (main settings audio llm conversation logging general voice-profiles device) do (
    if "!PANEL!"=="%%p" set "VALID=1"
)

if "!VALID!"=="0" (
    echo ❌ Invalid panel: !PANEL!
    echo Valid panels: main, settings, audio, llm, conversation, logging, general, voice-profiles, device
    exit /b 1
)

echo 🤖 Starting Jarvis Desktop Application
echo Panel: !PANEL!
echo Port: !PORT!
if not "!DEBUG_FLAG!"=="" echo Debug: Enabled
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if pywebview is installed
echo 🔄 Checking dependencies...
python -c "import webview" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  pywebview is not installed
    echo Installing pywebview...
    python -m pip install pywebview
    if errorlevel 1 (
        echo ❌ Failed to install pywebview
        echo Please install manually: pip install pywebview
        pause
        exit /b 1
    )
    echo ✅ pywebview installed successfully
) else (
    echo ✅ pywebview is available
)

REM Change to script directory
cd /d "%~dp0"

REM Launch the desktop app
echo 🚀 Launching Jarvis Desktop App...
python jarvis_app.py --panel "!PANEL!" --port "!PORT!" !DEBUG_FLAG!

if errorlevel 1 (
    echo.
    echo ❌ Desktop app failed to start
    pause
)

endlocal
