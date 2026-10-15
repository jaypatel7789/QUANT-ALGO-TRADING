# Registers Shark MT5 Sentinel as a 24/7 Windows Scheduled Task on the VPS

$TaskName = "SharkSentinel247"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ActionScript = Join-Path $ScriptDir "start_sentinel_cloud.bat"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Registering Shark MT5 Sentinel 24/7 Autostart Task      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Unregister if already existing
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$ActionScript`"" -WorkingDirectory $ScriptDir
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings

Write-Host "`n[SUCCESS] Task '$TaskName' has been registered to run on VPS Boot automatically!" -ForegroundColor Green
Write-Host "Your mobile command center will now run 24/7 uninterrupted." -ForegroundColor Yellow
