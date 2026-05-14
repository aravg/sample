@echo off
echo Starting Feedback Management System Frontend...
cd /d "%~dp0frontend"
python -m http.server 3000
echo Open http://localhost:3000 in your browser
pause
