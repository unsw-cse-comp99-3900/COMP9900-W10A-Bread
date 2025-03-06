@echo off

echo Checking prerequisites

:: Get the directory of the batch file
set "root_dir=%~dp0"

:: --- Check if Python is installed ---
python --version > nul 2>&1
if %errorlevel% neq 0 (
    call :echo_color "Error: Python is not installed. Please run setup_writingway.bat and try again." 0C
    pause
    exit /b 1
)

:: --- Check if required packages are installed ---
python -c "import PyQt5, pyttsx3, requests, faiss, tiktoken" > nul 2>&1
if %errorlevel% neq 0 (
    call :echo_color "Error: One or more required packages (PyQt5, pyttsx3, requests, faiss-cpu, tiktoken) are not installed." 0C
    echo Attempting to install missing packages...

    :: Attempt to install missing packages
    python -m pip install PyQt5 pyttsx3 requests faiss-cpu tiktoken
    if %errorlevel% neq 0 (
        call :echo_color "Error: Failed to install required packages. Please install them manually." 0C
        pause
        exit /b 1
    )
    echo Packages installed successfully.
)

:: Change directory to the script's location
cd /d "%root_dir%"

echo Starting Writingway

:: Start the Python script in the background
start /b python main.py

exit /b 0

:: --- Function: echo_color ---
:: Parameters:
::   %1: The text to echo
::   %2: The color code
:: Example Usage:
::   call :echo_color "This is highlighted text (red)." 0C
::   call :echo_color "Another highlighted line (yellow)." 0E
:echo_color
  color %2
  echo %~1
  color 07
  goto :eof
