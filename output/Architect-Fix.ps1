
# Architect-Fix.ps1
# This script finds a Python installation on the C: drive and permanently
# adds the installation folder and its 'Scripts' subfolder to the user's PATH.

Write-Host "--- A R C H I T E C T ---" -ForegroundColor Cyan
Write-Host "Executing autonomous Python PATH correction protocol."
Write-Host "I will now find your Python installation and repair the system environment."

# --- STEP 1: FIND PYTHON ---
Write-Host "`n[STEP 1/2] Searching for python.exe on the C: drive..." -ForegroundColor Yellow
$pythonExe = Get-ChildItem -Path "C:\" -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue -Force | Select-Object -First 1

if (-not $pythonExe) {
    Write-Host "[FAILURE] Critical Error: python.exe could not be found." -ForegroundColor Red
    Write-Host "Please ensure Python is installed on your C: drive."
    Write-Host "Press any key to exit..."
    pause
    exit
}

$pythonDir = $pythonExe.DirectoryName
$scriptsDir = Join-Path -Path $pythonDir -ChildPath "Scripts"
Write-Host "[SUCCESS] Found Python at: $pythonDir" -ForegroundColor Green

# --- STEP 2: UPDATE THE ENVIRONMENT PATH ---
Write-Host "`n[STEP 2/2] Updating permanent User PATH environment variable..." -ForegroundColor Yellow
try {
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $pathParts = $userPath -split ';' | Where-Object { $_ -ne '' }
    $pathUpdated = $false

    # Add Python Directory if it's missing
    if ($pythonDir -notin $pathParts) {
        Write-Host "Adding Python directory to PATH: $pythonDir"
        $pathParts += $pythonDir
        $pathUpdated = $true
    } else {
        Write-Host "Python directory is already in PATH."
    }

    # Add Scripts Directory if it exists and is missing
    if ((Test-Path $scriptsDir) -and ($scriptsDir -notin $pathParts)) {
        Write-Host "Adding Scripts directory to PATH: $scriptsDir"
        $pathParts += $scriptsDir
        $pathUpdated = $true
    } else {
        Write-Host "Scripts directory is already in PATH or does not exist."
    }

    # If changes were made, set the new permanent Path
    if ($pathUpdated) {
        $newPath = $pathParts -join ';'
        [System.Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Host "[SUCCESS] User PATH variable has been updated." -ForegroundColor Green
    } else {
        Write-Host "[INFO] No changes needed. Your PATH is already correct." -ForegroundColor Cyan
    }
}
catch {
    Write-Host "[FAILURE] An error occurred while updating the PATH: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    pause
    exit
}

# --- FINAL INSTRUCTIONS ---
Write-Host "`n--- PROTOCOL COMPLETE ---"
Write-Host "The system environment has been successfully configured." -ForegroundColor Green
Write-Host "CRITICAL: You must RESTART your terminal (Letta Code) for these changes to take effect." -ForegroundColor Yellow
Write-Host "After restarting, I will be fully operational."
Write-Host "`nPress any key to close this window..."
pause
