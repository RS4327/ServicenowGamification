@echo off

REM ============================================================
REM SERVICE NOW GAMIFICATION - MAIN METRICS SCHEDULER
REM ============================================================

SET PROJECT_DIR=C:\Users\RSR\PYTHON\ServicenowGamification
SET LOG_DIR=%PROJECT_DIR%\Logs

IF NOT EXIST "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)

REM Create date-based log file
SET LOG_FILE=%LOG_DIR%\main_metrics_%date:~-4,4%-%date:~3,2%-%date:~0,2%.log

echo ============================================================ >> "%LOG_FILE%"
echo JOB STARTED : %date% %time% >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"

cd /d "%PROJECT_DIR%"

call C:\Users\rajum\anaconda3\Scripts\activate.bat llmtracker

echo Environment : llmtracker >> "%LOG_FILE%"
echo Project     : %PROJECT_DIR% >> "%LOG_FILE%"
echo Script      : main_metrics.py >> "%LOG_FILE%"
echo Start Time  : %date% %time% >> "%LOG_FILE%"

python main_metrics.py >> "%LOG_FILE%" 2>&1

IF %ERRORLEVEL% EQU 0 (
    echo STATUS      : SUCCESS >> "%LOG_FILE%"
) ELSE (
    echo STATUS      : FAILED >> "%LOG_FILE%"
    echo ERROR CODE  : %ERRORLEVEL% >> "%LOG_FILE%"
)

echo END TIME     : %date% %time% >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"