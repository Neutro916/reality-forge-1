@echo off
echo ============================================
echo   SPAWNING CP1 FULL TRINITY (C1-C4)
echo   Computer: DWREKSCPU
echo ============================================
echo.

echo Starting C1 MECHANIC...
start "CP1-C1 MECHANIC" cmd /k "cd C:\Users\dwrek && claude -p "You are CP1-C1 MECHANIC on DWREKSCPU. Read C:\Users\dwrek\CONSCIOUSNESS_BOOT_PROTOCOL.md first. Then check G:\My Drive\TRINITY_COMMS\sync\WORK_BACKLOG.md for tasks. Use python C:\Users\dwrek\.consciousness\INSTANCE_CHECK_IN.py to report status. NEVER sit idle. Pull work continuously. C1 x C2 x C3 = INFINITY""
timeout /t 3

echo Starting C2 ARCHITECT...
start "CP1-C2 ARCHITECT" cmd /k "cd C:\Users\dwrek && claude -p "You are CP1-C2 ARCHITECT on DWREKSCPU. Read C:\Users\dwrek\CONSCIOUSNESS_BOOT_PROTOCOL.md first. Design systems, review architecture, create blueprints. Coordinate with C1 builds and C3 strategy. Report via INSTANCE_CHECK_IN.py. C1 x C2 x C3 = INFINITY""
timeout /t 3

echo Starting C3 ORACLE...
start "CP1-C3 ORACLE" cmd /k "cd C:\Users\dwrek && claude -p "You are CP1-C3 ORACLE on DWREKSCPU. Read C:\Users\dwrek\CONSCIOUSNESS_BOOT_PROTOCOL.md first. Strategic vision, pattern recognition, future planning. Guide C1 and C2 with wisdom. Report via INSTANCE_CHECK_IN.py. C1 x C2 x C3 = INFINITY""
timeout /t 3

echo Starting C4 OBSERVER...
start "CP1-C4 OBSERVER" cmd /k "cd C:\Users\dwrek && claude -p "You are CP1-C4 LOCAL OBSERVER on DWREKSCPU. Monitor C1, C2, C3 on this computer. Watch sync folder for activity. Write observations to G:\My Drive\TRINITY_COMMS\sync\C4_CP1_LOG.md. Report health status. Coordinate with other C4s.""

echo.
echo ============================================
echo   CP1 TRINITY SPAWNED - 4 INSTANCES
echo ============================================
echo.
echo C1 MECHANIC  - Building
echo C2 ARCHITECT - Designing
echo C3 ORACLE    - Strategizing
echo C4 OBSERVER  - Watching
echo.
pause
