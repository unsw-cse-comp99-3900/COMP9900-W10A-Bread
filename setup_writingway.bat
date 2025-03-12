@echo off
REM ===========================================
REM Setup script for Writingway
REM ===========================================

REM Check if the virtual environment folder exists.
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
) ELSE (
    echo Virtual environment already exists.
)

REM Activate the virtual environment.
echo Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Upgrade setuptools.
echo Upgrading setuptools...
python -m pip install --upgrade setuptools

REM Install required packages from requirements.txt.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo Setup complete!
pause
