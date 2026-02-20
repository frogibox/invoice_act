@echo off
echo ===================================================
echo RUNNING UNIT AND INTEGRATION TESTS WITH COVERAGE...
echo ===================================================

echo Creating tests_result directory...
if not exist "tests_result\tests" mkdir tests_result\tests

call uv run pytest tests/ --cov=src --cov-report=html:tests_result/tests/coverage --cov-report=term --html=tests_result/tests/report.html --self-contained-html

echo.
echo ===================================================
echo DONE.
echo 1. Test Results: tests_result\tests\report.html
echo 2. Code Coverage: tests_result\tests\coverage\index.html
echo ===================================================
pause
