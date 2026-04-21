@echo off
echo Installation des dependances...
pip install -r requirements.txt --quiet
echo.
echo Demarrage du serveur...
python server.py
pause
