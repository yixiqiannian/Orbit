@echo off
echo Starting Orbit Backend...
start "Orbit Backend" cmd /k "cd /d G:\Orbit\backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3

echo Starting Orbit Frontend...
start "Orbit Frontend" cmd /k "cd /d G:\Orbit\frontend && npm run dev"

echo Orbit is starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5174
echo.
echo Press any key to exit this window...
pause > nul
