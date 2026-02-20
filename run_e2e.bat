@echo off
echo ===================================================
echo RUNNING E2E TESTS WITH REPORT...
echo ===================================================

echo Creating reports directory...
if not exist "e2e_reports" mkdir e2e_reports

echo Starting backend on port 10000...
start /B uv run uvicorn src.main:app --host 127.0.0.1 --port 10000 > server.log 2>&1
echo Waiting for server to start...

:wait_server
timeout /t 1 >nul
curl -s http://localhost:10000/ >nul 2>&1
if errorlevel 1 (
    echo Still waiting...
    goto wait_server
)
echo Server is ready!

echo Running E2E tests with report...
uv run pytest e2e/ --html=e2e_reports/e2e_report.html --self-contained-html --tb=short

echo Stopping server on port 10000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :10000 ^| findstr LISTENING') do taskkill /PID %%a /F >nul 2>&1

echo.
echo ===================================================
echo DONE.
echo Report saved to: e2e_reports/e2e_report.html
echo ===================================================
pause
