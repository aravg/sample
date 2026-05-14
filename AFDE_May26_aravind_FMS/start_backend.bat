@echo off
echo Starting Feedback Management System Backend...
cd /d "%~dp0backend"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
