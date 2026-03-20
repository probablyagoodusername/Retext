@echo off
echo Building Retext...
cd /d "%~dp0.."
pip install pyinstaller
pyinstaller --onefile --windowed --name Retext --icon assets\icon.ico --add-data "assets;assets" src\rewrite\main.py
echo.
echo Build complete! Output: dist\Retext.exe
pause
