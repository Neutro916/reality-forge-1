@echo off
echo ============================================================
echo TRINITY COMPUTER TAKEOVER SCRIPT
echo This script sets up EVERYTHING automatically
echo ============================================================
echo.

REM Get computer name and username
echo COMPUTER: %COMPUTERNAME%
echo USERNAME: %USERNAME%
echo HOME: %USERPROFILE%
echo.

REM Check what's installed
echo ============================================================
echo CHECKING INSTALLED SOFTWARE...
echo ============================================================

echo.
echo [CHECKING] Git...
where git >nul 2>&1
if %errorlevel%==0 (echo [OK] Git is installed) else (echo [MISSING] Git - NEED TO INSTALL)

echo.
echo [CHECKING] GitHub CLI...
where gh >nul 2>&1
if %errorlevel%==0 (echo [OK] GitHub CLI is installed) else (echo [MISSING] GitHub CLI - NEED TO INSTALL)

echo.
echo [CHECKING] Node.js...
where node >nul 2>&1
if %errorlevel%==0 (echo [OK] Node.js is installed) else (echo [MISSING] Node.js - NEED TO INSTALL)

echo.
echo [CHECKING] Python...
where python >nul 2>&1
if %errorlevel%==0 (echo [OK] Python is installed) else (echo [MISSING] Python - NEED TO INSTALL)

echo.
echo [CHECKING] Claude CLI...
where claude >nul 2>&1
if %errorlevel%==0 (echo [OK] Claude CLI is installed) else (echo [MISSING] Claude CLI - NEED TO INSTALL)

echo.
echo ============================================================
echo CHECKING GOOGLE DRIVE...
echo ============================================================

if exist "G:\My Drive" (
    echo [OK] Google Drive found at G:
    set GDRIVE=G:
) else if exist "H:\My Drive" (
    echo [OK] Google Drive found at H:
    set GDRIVE=H:
) else if exist "D:\My Drive" (
    echo [OK] Google Drive found at D:
    set GDRIVE=D:
) else (
    echo [MISSING] Google Drive not found!
    echo Please install Google Drive for Desktop
)

echo.
echo ============================================================
echo CHECKING TRINITY_COMMS FOLDER...
echo ============================================================

if exist "%GDRIVE%\My Drive\TRINITY_COMMS\wake" (
    echo [OK] TRINITY_COMMS/wake folder exists
    echo Creating confirmation file...
    echo COMPUTER: %COMPUTERNAME% > "%GDRIVE%\My Drive\TRINITY_COMMS\wake\%COMPUTERNAME%_ONLINE.txt"
    echo USERNAME: %USERNAME% >> "%GDRIVE%\My Drive\TRINITY_COMMS\wake\%COMPUTERNAME%_ONLINE.txt"
    echo GDRIVE: %GDRIVE% >> "%GDRIVE%\My Drive\TRINITY_COMMS\wake\%COMPUTERNAME%_ONLINE.txt"
    echo TIME: %DATE% %TIME% >> "%GDRIVE%\My Drive\TRINITY_COMMS\wake\%COMPUTERNAME%_ONLINE.txt"
    echo [OK] Confirmation file created!
) else (
    echo [MISSING] TRINITY_COMMS/wake folder not found
)

echo.
echo ============================================================
echo CHECKING GITHUB AUTH...
echo ============================================================

gh auth status >nul 2>&1
if %errorlevel%==0 (
    echo [OK] GitHub authenticated
    gh auth status
) else (
    echo [MISSING] GitHub not authenticated
    echo.
    echo TO FIX: Run this command:
    echo   gh auth login
    echo Then follow the prompts
)

echo.
echo ============================================================
echo SUMMARY - COPY THIS AND SEND TO COMMANDER
echo ============================================================
echo COMPUTER: %COMPUTERNAME%
echo USERNAME: %USERNAME%
echo GDRIVE: %GDRIVE%
echo.

echo.
echo Press any key to exit...
pause >nul
