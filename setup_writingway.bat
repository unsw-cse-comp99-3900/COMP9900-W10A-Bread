
@echo off

:: Set the temporary directory for installers
set "temp_dir=installer_temp"

:: Create the temporary directory
if not exist "%temp_dir%" mkdir "%temp_dir%"



:: --- Check if Python is already installed ---

python --version > nul 2>&1
if %errorlevel% equ 0 (
    echo Python is already installed.
    goto :check_pip
)

call :echo_color "Python is not installed. Proceeding with download and installation..." 0C
:: --- Choose Python version and architecture (IMPORTANT!) ---

set "python_version=3.13.2"
set "installer_url=https://www.python.org/ftp/python/%python_version%/python-%python_version%-amd64.exe"
:: https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe
set "installer_name=%temp_dir%\python_installer.exe"


:: --- Download Python Installer ---

echo Downloading Python installer...
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%installer_url%', '%installer_name%')"

if %errorlevel% neq 0 (
	call :echo_color "Download failed.  Check your internet connection and the installer URL." 0C
    goto :end
)

echo Download complete.

:: --- Install Python (Silently) ---

echo Installing Python...
call :echo_color "Please click Yes on the User Account Control (UAC) prompt that appears.  This is required to install Python for all users.  The UAC prompt may be minimized or behind other windows, so check your taskbar." 0E

%installer_name% /quiet InstallAllUsers=1 PrependPath=1

if %errorlevel% neq 0 (
	call :echo_color "Installation failed." 0C
    goto :end
)

echo Python installation complete.

:: --- Verify Python Installation ---
timeout /t 5 /nobreak > nul

python --version > nul 2>&1
if %errorlevel% neq 0 (
	call :echo_color "Python installation may have failed.  Please check manually." 0E
    goto :end
)

:check_pip
:: --- Check if pip is installed ---

echo Checking for pip...
python -m pip --version > nul 2>&1
if %errorlevel% equ 0 (
    echo pip is already installed.
    goto :end
)

call :echo_color "pip is not installed.  Proceeding with download and installation..." 0E

:: --- Download get-pip.py ---

set "get_pip_url=https://bootstrap.pypa.io/get-pip.py"
set "get_pip_script=get-pip.py"

echo Downloading get-pip.py...
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%get_pip_url%', '%get_pip_script%')"

if %errorlevel% neq 0 (
	call :echo_color "Download of get-pip.py failed. Check your internet connection." 0C
    goto :end
)

echo Download complete.

:: --- Install pip ---

echo Installing pip...
python %get_pip_script%

if %errorlevel% neq 0 (
	call :echo_color "pip installation failed." 0C
    goto :end
)

echo pip installation complete.

:: --- Verify pip Installation ---

python -m pip --version > nul 2>&1
if %errorlevel% equ 0 (
    echo pip is installed and working correctly.
) else (
	call :echo_color "pip installation may have failed. Please check manually." 0C
)


:install_packages
:: --- Install required packages ---

echo Installing required packages (PyQt5, pyttsx3, requests)...

:: Use a single pip install command for efficiency
python -m pip install PyQt5 pyttsx3 requests

if %errorlevel% neq 0 (
	call :echo_color "Package installation failed." 0C
    goto :end
)

echo Packages installed successfully.


:: --- Cleanup (Optional) ---
del /f /q "%installer_name%"
del /f /q "%get_pip_script%"

:: Delete the temporary directory
rd /s /q "%temp_dir%"


:end
echo Setup Done. Python and all dependancies are installed.
pause


goto :eof  :: Important! Prevents falling through into the function

:: --- Function: echo_color ---
:: Parameters:
::   %1: The text to echo
::   %2: The color code
:: Example Usage:
:: Call the function to print highlighted text
:: call :echo_color "This is highlighted text (red)." 0C
:: call :echo_color "Another highlighted line (yellow)." 0E
:echo_color
  color %2
  echo %~1
  color 07
  goto :eof
:: --- End of Function ---

