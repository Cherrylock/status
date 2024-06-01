@echo off
echo Installing required packages...
pip install -r requirements.txt

echo Starting the bot...
python status.py

pause
