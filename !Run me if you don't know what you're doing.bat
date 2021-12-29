@ECHO OFF

:: Detect if python is installed
python --version 2>NUL
IF errorlevel 1 (
    ECHO "Python is not installed. Please install it and run again."
    PAUSE
    EXIT /b 1
)

:: First time setup (pip requirements)
pip -q install -r requirements.txt

python main.py

ECHO To run this again next time, just run main.py, also feel free to delete this file.
PAUSE