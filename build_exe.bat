@echo off
pip install pyinstaller
pyinstaller --noconsole --onefile --name "jrz-Accessory-Tool" src\jrz_accessorys_tool.py
echo.
echo Done. Your exe is in the dist folder.
pause
