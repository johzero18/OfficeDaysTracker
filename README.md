# Office Attendance Tracker

Automated office attendance tracking system based on WiFi network detection.

**Multi-platform support:**
- 🍎 **macOS** → See [iOS/README.md](iOS/README.md)
- 🪟 **Windows** → See [Windows/README.md](Windows/README.md)

---

## 📁 Project Structure

```
control-oficina/
├── iOS/                    # macOS version (LaunchAgent)
│   ├── check_wifi.sh      # Detection script (Bash)
│   ├── setup.sh           # Installation script
│   ├── view_report.command # Dashboard launcher
│   ├── show_attendance.sh # Terminal stats
│   ├── report.html        # Web dashboard
│   └── ...
│
├── Windows/               # Windows version (Task Scheduler)
│   ├── check_wifi.ps1     # Detection script (PowerShell)
│   ├── setup.bat          # Installation script
│   ├── view_report.bat    # Dashboard launcher
│   ├── report.html        # Web dashboard
│   └── ...
│
└── README.md              # This file
```

---

## 🚀 Quick Start

### macOS
```bash
cd iOS/
./setup.sh
```
Then double-click `view_report.command`

### Windows
1. Open `Windows\` folder
2. Double-click `setup.bat`
3. Follow instructions
4. Double-click `view_report.bat` to view dashboard

---

## 📊 Dashboard Features

Both macOS and Windows versions include a web dashboard with:
- 📊 Monthly progress toward 8 required days
- 📅 Total days and current month summary
- 🗓️ Next Argentina holiday (via API)
- 📈 Monthly summaries with charts
- 🕐 Last 10 attendance days
- 🔄 **Auto-refresh every 30 seconds**
- 🎨 Boehringer Ingelheim corporate branding

---

## 🔧 Configuration

### Change office gateway

**macOS**: Edit [iOS/check_wifi.sh](iOS/check_wifi.sh#L8)
```bash
OFFICE_GATEWAY="YOUR_GATEWAY_HERE"
```

**Windows**: Edit [Windows/check_wifi.ps1](Windows/check_wifi.ps1#L8)
```powershell
$OFFICE_GATEWAY = "YOUR_GATEWAY_HERE"
```

### View detection logs

**macOS**:
```bash
tail -f iOS/tracker.log
```

**Windows**:
```cmd
notepad Windows\tracker.log
```

```bash
cat tracker.log
```

### Probar manualmente

```bash
./check_wifi.sh
cat attendance.json
---

## ✨ Features

- ✅ **Automatic detection**: Detects office network via gateway (10.15.16.1)
- ✅ **Multi-platform**: macOS (LaunchAgent) and Windows (Task Scheduler)
- ✅ **Real-time dashboard**: Dynamic HTML with Boehringer Ingelheim branding
- ✅ **Holidays API**: Uses ArgentinaDatos API for updated holidays
- ✅ **Workday calculation**: Excludes weekends and holidays
- ✅ **Portable**: Works in any folder without hardcoded paths
- ✅ **No external database**: Uses simple JSON file

---

## 🔧 Troubleshooting

### Dashboard doesn't load
Make sure to double-click the launcher script (not open HTML directly).
This starts a local web server needed to avoid CORS browser restrictions.

**macOS**: `view_report.command`
**Windows**: `view_report.bat`

### Check current gateway

**macOS**:
```bash
route -n get default | grep gateway
```

**Windows**:
```cmd
ipconfig | findstr "Gateway"
```

---

## 🔍 How It Works

1. **Automatic detection**: Script checks network gateway every 30 minutes
2. **Identification**: Looks for office gateway (10.15.16.1 for BI-Mobile)
3. **Unique registration**: Saves only one entry per day in `attendance.json`
4. **Notification**: Alerts you when attendance is registered
5. **Dynamic dashboard**: Reads JSON in real-time and displays updated stats

---

## ⚙️ Advanced Configuration

### Disable auto-execution

**macOS**:
```bash
launchctl unload ~/Library/LaunchAgents/com.office-tracker.plist
```

**Windows**:
```cmd
schtasks /delete /tn "OfficeTracker" /f
```

### Enable auto-execution

**macOS**:
```bash
launchctl load ~/Library/LaunchAgents/com.office-tracker.plist
```

**Windows**:
```cmd
schtasks /create /tn "OfficeTracker" /tr "powershell -ExecutionPolicy Bypass -File C:\path\to\check_wifi.ps1" /sc minute /mo 30 /f
```

### Change check frequency

**macOS**: Edit `~/Library/LaunchAgents/com.office-tracker.plist`:
```xml
<key>StartInterval</key>
<integer>1800</integer>  <!-- 1800 = 30 minutes -->
```

**Windows**: Modify task schedule:
```cmd
schtasks /create /tn "OfficeTracker" /tr "..." /sc minute /mo 15 /f
```

### Detect multiple office networks

**macOS**: Edit [iOS/check_wifi.sh](iOS/check_wifi.sh):
```bash
if [ "$CURRENT_GATEWAY" = "10.15.16.1" ] || [ "$CURRENT_GATEWAY" = "OTHER_GATEWAY" ]; then
```

**Windows**: Edit [Windows/check_wifi.ps1](Windows/check_wifi.ps1):
```powershell
if ($gateway -eq "10.15.16.1" -or $gateway -eq "OTHER_GATEWAY") {
```

---

## 📝 Files

### macOS (iOS folder)
| File | Description |
|------|-------------|
| `setup.sh` | Automated installation script |
| `check_wifi.sh` | Main network detection script |
| `show_attendance.sh` | Terminal statistics viewer |
| `view_report.command` | Web dashboard launcher |
| `report.html` | Dynamic HTML dashboard |
| `tracker.log` | Detection history |

### Windows folder
| File | Description |
|------|-------------|
| `setup.bat` | Automated installation script |
| `check_wifi.ps1` | Main network detection script (PowerShell) |
| `view_report.bat` | Web dashboard launcher |
| `report.html` | Dynamic HTML dashboard |
| `tracker.log` | Detection history |

### Shared
- `attendance.json` - Database (JSON)
- `Boehringer_Logo_RGB_Accent-Green.svg` - Corporate logo

---

## 🌐 APIs Used

- **ArgentinaDatos API**: `https://api.argentinadatos.com/v1/feriados/YYYY`
  - Official Argentina holidays
  - Includes fixed, movable, and tourist bridge holidays
  - Automatic updates

---

## 🔒 Privacy

- ✅ All data stored locally in `attendance.json`
- ✅ No information sent to external servers
- ✅ Only queries public holidays API (anonymous)
- ✅ No credentials or authentication required

---

## 📝 Archivos del Sistema

| Archivo | Descripción |
|---------|-------------|
| `setup.sh` | Script de instalación (ejecutar primero) |
| `check_wifi.sh` | Script principal de detección |
| `show_attendance.sh` | Visualización de estadísticas |
| `attendance.json` | Base de datos (se crea automáticamente) |
| `tracker.log` | Historial de detecciones |
| `error.log` | Errores del sistema |