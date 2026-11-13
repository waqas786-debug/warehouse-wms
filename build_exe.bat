@echo off
echo Installing PyInstaller and Waitress...
pip install pyinstaller waitress
echo Building Standalone Offline WMS Executable...
pyinstaller --noconfirm --onefile --console ^
  --name "WarehouseWMS_Offline" ^
  --add-data "app/templates;app/templates" ^
  --add-data "app/static;app/static" ^
  --hidden-import "sqlalchemy.sql.default_comparator" ^
  run_local.py
echo Build Complete! Check dist\WarehouseWMS_Offline.exe
pause
