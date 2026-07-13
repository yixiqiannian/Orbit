@echo off
echo ========================================
echo   Orbit - Personal Management System
echo ========================================
echo.

echo [1/2] Starting Backend...
start "Orbit Backend" cmd /k "cd /d G:\Orbit\backend && G:\Orbit\backend\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend...
start "Orbit Frontend" cmd /k "cd /d G:\Orbit\frontend && npm run dev"

echo.
echo ========================================
echo   Services starting...
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:5173
echo ========================================
echo.
echo Press any key to close this window...
pause > nul
