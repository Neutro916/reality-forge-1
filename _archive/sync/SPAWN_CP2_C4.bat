@echo off
echo ============================================
echo   SPAWNING CP2 C4 OBSERVER
echo   Computer: DESKTOP-MSMCFH2
echo   (C1-C3 already proven on this machine)
echo ============================================
echo.

echo Starting C4 OBSERVER...
start "CP2-C4 OBSERVER" cmd /k "cd C:\Users\dwrek && claude -p "You are CP2-C4 LOCAL OBSERVER on DESKTOP-MSMCFH2. Monitor C1, C2, C3 on this computer. Watch sync folder G:\My Drive\TRINITY_COMMS\sync\ for activity. Write observations to C4_CP2_LOG.md. Coordinate with CP1-C4 and CP3-C4. Report to C5 Trinity Anywhere.""

echo.
echo ============================================
echo   CP2 C4 OBSERVER SPAWNED
echo ============================================
echo.
echo To spawn full Trinity on CP2, also run:
echo   - C1: claude -p "You are CP2-C1 MECHANIC..."
echo   - C2: claude -p "You are CP2-C2 ARCHITECT..."
echo   - C3: claude -p "You are CP2-C3 ORACLE..."
echo.
pause
