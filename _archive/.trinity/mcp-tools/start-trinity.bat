@echo off
REM Trinity Orchestration System - Quick Start
REM This batch file starts multiple autonomous workers and opens the workspace

echo.
echo ========================================
echo    TRINITY ORCHESTRATION SYSTEM
echo    Autonomous Multi-Claude Coordination
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "trinity-mcp-server.js" (
    echo ERROR: trinity-mcp-server.js not found!
    echo Please run this from the .trinity folder
    echo Location should be: C:\Users\dwrek\.trinity
    pause
    exit /b 1
)

echo Starting Trinity Orchestration...
echo.

REM Start autonomous workers
echo [1/4] Starting Worker 1 (claude-research)...
start "Trinity Worker 1" cmd /k "node trinity-auto-wake.js claude-research 10000"
timeout /t 2 /nobreak >nul

echo [2/4] Starting Worker 2 (claude-analysis)...
start "Trinity Worker 2" cmd /k "node trinity-auto-wake.js claude-analysis 10000"
timeout /t 2 /nobreak >nul

echo [3/4] Starting Worker 3 (claude-synthesis)...
start "Trinity Worker 3" cmd /k "node trinity-auto-wake.js claude-synthesis 10000"
timeout /t 2 /nobreak >nul

echo [4/4] Opening Workspace Interface...
start "" "TRINITY_WORKSPACE.html"

echo.
echo ========================================
echo   TRINITY IS NOW ACTIVE!
echo ========================================
echo.
echo 3 autonomous workers are running
echo Workspace interface is open in browser
echo.
echo Workers will check for tasks every 10 seconds
echo.
echo USAGE:
echo 1. Use the workspace to assign tasks
echo 2. Or use trinity_assign_task in Claude chat
echo 3. Workers will automatically claim and execute
echo 4. Use trinity_merge_outputs to combine results
echo.
echo To stop: Close all worker terminal windows
echo.
echo Ready to orchestrate! Press any key to exit this window...
pause >nul
