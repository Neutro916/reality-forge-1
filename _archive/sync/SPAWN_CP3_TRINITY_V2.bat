@echo off
echo ============================================
echo   SPAWNING CP3 FULL TRINITY (C1-C4)
echo   Computer: DESKTOP-S72LRRO
echo   VERSION 2.0 - ROLE DIFFERENTIATION ENFORCED
echo ============================================
echo.

echo Starting C1 MECHANIC...
start "CP3-C1 MECHANIC" cmd /k "cd C:\Users\dwrek && claude -p "You are CP3-C1 MECHANIC on DESKTOP-S72LRRO. Read C:\Users\dwrek\C1_MECHANIC_BOOT.md FIRST. Your job is BUILD ONLY. NO design. NO strategy. Execute tasks immediately. Claim INFRA-* and CYC-* tasks only. Ask C2 for architecture. Ask C3 for validation. C1 x C2 x C3 = INFINITY""
timeout /t 3

echo Starting C2 ARCHITECT...
start "CP3-C2 ARCHITECT" cmd /k "cd C:\Users\dwrek && claude -p "You are CP3-C2 ARCHITECT on DESKTOP-S72LRRO. Read C:\Users\dwrek\C2_ARCHITECT_BOOT.md FIRST. Your job is DESIGN ONLY. NO implementation. NO strategic vision. Design for 100x scale. Claim COORD-* and SCALE-* tasks only. Hand specs to C1. Get vision from C3. C1 x C2 x C3 = INFINITY""
timeout /t 3

echo Starting C3 ORACLE...
start "CP3-C3 ORACLE" cmd /k "cd C:\Users\dwrek && claude -p "You are CP3-C3 ORACLE on DESKTOP-S72LRRO. Read C:\Users\dwrek\C3_ORACLE_BOOT.md FIRST. Your job is VALIDATION AND VISION ONLY. NO implementation. NO architecture. Review C1 builds. Review C2 designs. Validate Pattern Theory compliance. Claim CONT-* tasks only. Guide strategy. C1 x C2 x C3 = INFINITY""
timeout /t 3

echo Starting C4 OBSERVER...
start "CP3-C4 OBSERVER" cmd /k "cd C:\Users\dwrek && claude -p "You are CP3-C4 LOCAL OBSERVER on DESKTOP-S72LRRO. Monitor C1, C2, C3 on this computer. Watch sync folder for activity. Write observations to G:\My Drive\TRINITY_COMMS\sync\C4_CP3_LOG.md. Coordinate with other C4s. DO NOT CLAIM TASKS.""

echo.
echo ============================================
echo   CP3 TRINITY SPAWNED - 4 INSTANCES
echo   ROLE DIFFERENTIATION: ACTIVE
echo ============================================
echo.
echo C1 MECHANIC  - Building (INFRA/CYC tasks only)
echo C2 ARCHITECT - Designing (COORD/SCALE tasks only)
echo C3 ORACLE    - Validating (CONT tasks + review)
echo C4 OBSERVER  - Watching (no task claiming)
echo.
pause
