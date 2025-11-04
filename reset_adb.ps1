# ADB Connection Reset Script
# Used to clean up adb connection state after Ctrl+C exit
# Usage: .\reset_adb.ps1 [adb_path]
# Example: .\reset_adb.ps1 "D:\platform-tools\adb.exe"

param(
    [string]$adb_path = "adb"
)

Write-Host "Resetting ADB connection..." -ForegroundColor Yellow
Write-Host "Using ADB path: $adb_path" -ForegroundColor Gray

Write-Host "`n1. Stopping ADB server..." -ForegroundColor Cyan
& $adb_path kill-server
Start-Sleep -Seconds 1

Write-Host "`n2. Starting ADB server..." -ForegroundColor Cyan
& $adb_path start-server
Start-Sleep -Seconds 2

Write-Host "`n3. Checking device connection status..." -ForegroundColor Cyan
& $adb_path devices

Write-Host "`n4. Attempting to reconnect device..." -ForegroundColor Cyan
& $adb_path reconnect
Start-Sleep -Seconds 1

Write-Host "`n5. Final device status:" -ForegroundColor Cyan
& $adb_path devices

Write-Host "`n[OK] ADB connection reset completed!" -ForegroundColor Green
