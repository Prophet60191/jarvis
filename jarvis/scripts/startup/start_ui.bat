@echo off
REM Jarvis Web UI Launcher for Windows
REM Quick start batch file for the Jarvis Voice Assistant Web Configuration Interface

echo.
echo 🤖 Jarvis Web UI Launcher
echo ========================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ and add it to your PATH.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if start_ui.py exists
if not exist "start_ui.py" (
    echo ❌ start_ui.py not found! Please run this from the Jarvis project directory.
    pause
    exit /b 1
)

REM Parse command line arguments or use defaults
set PANEL=main
set PORT=8080

if "%1"=="--help" goto :help
if "%1"=="-h" goto :help
if "%1"=="help" goto :help

if "%1"=="settings" set PANEL=settings
if "%1"=="audio" set PANEL=audio
if "%1"=="llm" set PANEL=llm
if "%1"=="conversation" set PANEL=conversation
if "%1"=="logging" set PANEL=logging
if "%1"=="general" set PANEL=general
if "%1"=="voice-profiles" set PANEL=voice-profiles
if "%1"=="device" set PANEL=device

echo 🚀 Starting Jarvis Web Interface...
echo    Panel: %PANEL%
echo    Port: %PORT%
echo    URL: http://localhost:%PORT%
echo.

REM Launch the UI
python start_ui.py --panel %PANEL% --port %PORT%

goto :end

:help
echo.
echo Usage: start_ui.bat [panel]
echo.
echo Available panels:
echo   main           Dashboard overview (default)
echo   settings       Configuration overview
echo   audio          Audio and TTS settings
echo   llm            Language model configuration
echo   conversation   Conversation flow settings
echo   logging        Logging configuration
echo   general        General application settings
echo   voice-profiles Voice cloning management
echo   device         Device and hardware information
echo.
echo Examples:
echo   start_ui.bat                # Launch main dashboard
echo   start_ui.bat settings       # Launch settings overview
echo   start_ui.bat audio          # Launch audio configuration
echo.
echo For advanced options, use:
echo   python start_ui.py --help
echo.
pause
goto :end

:end
