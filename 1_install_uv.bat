@echo off
echo Installing UV package manager...
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
echo UV installation completed!
echo.
echo Checking UV installation...
uv --version
if %ERRORLEVEL% EQU 0 (
    echo UV installed successfully!
) else (
    echo UV installation failed. Please check the error messages above.
)
pause