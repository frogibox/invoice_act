@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"

echo ========================================
echo    WARNING: ALL DATA WILL BE DELETED!
echo ========================================
echo.
echo Press Y to continue,
echo or press Enter to cancel.
echo.
set /p confirm="Are you sure? This is IRREVERSIBLE! (Y/Enter): "

if /i not "%confirm%"=="Y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

if not exist "database.db" (
    echo Database file not found. Nothing to clean.
    pause
    exit /b 0
)

echo Creating backup...
if not exist "backups" mkdir backups

set datetime=%date:~6,4%-%date:~3,2%-%date:~0,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
set datetime=%datetime: =0%

copy "database.db" "backups\db_backup_%datetime%.db"

if %errorlevel% neq 0 (
    echo Failed to create backup.
    pause
    exit /b 1
)

echo Backup created: backups\db_backup_%datetime%.db
echo.

echo ========================================
echo    CLEAR STOP WORDS TABLE?
echo ========================================
echo.
echo Press Y to clear stop words table,
echo or press Enter to keep stop words.
echo.
set /p clear_stop_words="Clear stop words table? (Y/Enter): "

set clear_stop_words=%clear_stop_words:~0,1%
if /i "%clear_stop_words%"=="Y" (
    set keep_stop_words=False
    echo Stop words table WILL be cleared.
) else (
    set keep_stop_words=True
    echo Stop words table will be kept.
)

echo.
echo ========================================
echo    CLEAR EMPLOYEES TABLE?
echo ========================================
echo.
echo Press Y to clear employees table,
echo or press Enter to keep employees.
echo.
set /p clear_employees="Clear employees table? (Y/Enter): "

set clear_employees=%clear_employees:~0,1%
if /i "%clear_employees%"=="Y" (
    set keep_employees=False
    echo Employees table WILL be cleared.
) else (
    set keep_employees=True
    echo Employees table will be kept.
)

echo.
echo Deleting database...
del "database.db"

if %errorlevel% neq 0 (
    echo Failed to delete database.
    pause
    exit /b 1
)

echo Database deleted. Reinitializing...

if "%keep_employees%"=="True" (
    if "%keep_stop_words%"=="True" (
        .venv\Scripts\python.exe -c "from src.database import init_db, get_session, Employee, StopWord; init_db(); session = get_session(); session.query(Employee).delete(); session.query(StopWord).delete(); session.commit(); session.close()"
    ) else (
        .venv\Scripts\python.exe -c "from src.database import init_db, get_session, Employee; init_db(); session = get_session(); session.query(Employee).delete(); session.commit(); session.close()"
    )
) else (
    if "%keep_stop_words%"=="True" (
        .venv\Scripts\python.exe -c "from src.database import init_db, get_session, StopWord; init_db(); session = get_session(); session.query(StopWord).delete(); session.commit(); session.close()"
    ) else (
        .venv\Scripts\python.exe -c "from src.database import init_db; init_db()"
    )
)

if %errorlevel% neq 0 (
    echo Failed to initialize database.
    pause
    exit /b 1
)

echo.
echo Database cleaned and reinitialized successfully!
pause
