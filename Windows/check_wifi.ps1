# Office Attendance Tracker - WiFi Detection Script (Windows)
# Detects if you're connected to office network and registers attendance
# 
# Method: Detects network gateway (10.15.16.1 = BI-Mobile office)

# Office gateway (BI-Mobile)
$OFFICE_GATEWAY = "10.15.16.1"

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$DATA_FILE = Join-Path $SCRIPT_DIR "attendance.json"
$LOG_FILE = Join-Path $SCRIPT_DIR "tracker.log"

# Logging function
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] $Message" | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8
}

# Create JSON file if it doesn't exist
if (-not (Test-Path $DATA_FILE)) {
    '{"dates":[]}' | Out-File -FilePath $DATA_FILE -Encoding UTF8
    Write-Log "Attendance file created"
}

# Get current gateway
try {
    $gateway = (Get-NetRoute -DestinationPrefix "0.0.0.0/0" | Get-NetIPConfiguration | Select-Object -ExpandProperty IPv4DefaultGateway).NextHop
    Write-Log "Gateway detected: '$gateway'"
} catch {
    Write-Log "Error getting gateway: $_"
    exit 1
}

# Check if we're in office network
if ($gateway -eq $OFFICE_GATEWAY) {
    $TODAY = Get-Date -Format "yyyy-MM-dd"
    
    # Read JSON file
    $jsonContent = Get-Content $DATA_FILE -Raw | ConvertFrom-Json
    
    # Check if already registered today
    if ($jsonContent.dates -contains $TODAY) {
        Write-Log "Already registered today ($TODAY)"
    } else {
        # Add today's date
        $jsonContent.dates = @($TODAY) + $jsonContent.dates
        
        # Save JSON
        $jsonContent | ConvertTo-Json -Depth 10 | Out-File -FilePath $DATA_FILE -Encoding UTF8
        Write-Log "✓ Attendance registered: $TODAY"
        
        # Notification (Windows 10/11)
        Add-Type -AssemblyName System.Windows.Forms
        $notification = New-Object System.Windows.Forms.NotifyIcon
        $notification.Icon = [System.Drawing.SystemIcons]::Information
        $notification.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
        $notification.BalloonTipText = "Attendance registered for today"
        $notification.BalloonTipTitle = "Office Tracker"
        $notification.Visible = $true
        $notification.ShowBalloonTip(3000)
        Start-Sleep -Seconds 3
        $notification.Dispose()
    }
} else {
    Write-Log "Not connected to office (gateway: $gateway)"
}
