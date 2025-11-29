@echo off
echo Running Backend Tests with venv...
REM Ensure we are using the virtual environment python
.\backend\venv\Scripts\python -m pytest backend/tests %*
if %ERRORLEVEL% NEQ 0 (
    echo Tests Failed!
    exit /b %ERRORLEVEL%
)
echo Tests Passed!
