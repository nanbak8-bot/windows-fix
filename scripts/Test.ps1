Write-Host "Hello from PowerShell!"
$svc = 'Spooler'
Write-Host "Restarting service: $svc"
try {
  Restart-Service -Name $svc -Force -ErrorAction Stop
  Write-Host "Service $svc restarted successfully."
} catch {
  Write-Error "Failed to restart $svc: $($_.Exception.Message)"
}
