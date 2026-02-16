@echo off
echo ========================================
echo    Restore Database from Backup
echo ========================================
echo.

if not exist "backups\" (
    echo No backups found.
    pause
    exit /b 0
)

setlocal EnableDelayedExpansion

set count=0
set "files[0]=dummy"

echo Available backups:
echo.

for %%f in (backups\*.db) do (
    set /a count+=1
    set files[!count!]=%%f
    echo [!count!] - %%~nf
)

echo.

if %count%==0 (
    echo No backups found.
    pause
    exit /b 0
)

set /p backup_num="Enter backup number to restore: "

if "%backup_num%"=="" (
    echo No backup selected.
    pause
    exit /b 1
)

set "selected=!files[%backup_num%]!"

if "%selected%"=="" (
    echo Invalid backup number.
    pause
    exit /b 1
)

echo.
echo Restoring from: !selected!
echo.

if exist "database.db" (
    echo Deleting current database...
    del "database.db"
)

copy "!selected!" "database.db"

if %errorlevel% neq 0 (
    echo Failed to restore database.
    pause
    exit /b 1
)

echo.
echo Database restored successfully!
pause
