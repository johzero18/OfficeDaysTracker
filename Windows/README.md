# Office Attendance Tracker - Windows Version

Sistema de tracking automático de asistencia a oficina basado en detección de red WiFi para Windows.

---

## 🚀 Instalación Rápida

### 1. Requisitos
- **Windows 10/11**
- **PowerShell** (viene preinstalado)
- **Python 3** (para el dashboard web)
  - Descargar desde: https://www.python.org/downloads/

### 2. Ejecutar Setup
1. Doble clic en **`setup.bat`**
2. Seguir las instrucciones en pantalla
3. Responder "Y" para activar ejecución automática

### 3. ¡Listo!
El sistema detectará automáticamente cuando estés conectado a la red de oficina (BI-Mobile).

---

## 📊 Ver Dashboard

**Doble clic en `view_report.bat`** para abrir el dashboard web con:
- 📊 Progreso mensual hacia 8 días obligatorios
- 📅 Días totales y del mes actual
- 🗓️ Próximo feriado argentino
- 📈 Resumen por mes con gráficos
- 🕐 Últimos 10 días registrados
- 🔄 Actualización automática cada 30 segundos

---

## ⚙️ Configuración

### Cambiar gateway de oficina
Edita `check_wifi.ps1` línea 8:
```powershell
$OFFICE_GATEWAY = "TU_GATEWAY_AQUI"
```

### Ver logs
```cmd
notepad tracker.log
```

### Probar manualmente
```cmd
powershell -ExecutionPolicy Bypass -File check_wifi.ps1
```

### Desactivar ejecución automática
```cmd
schtasks /delete /tn "OfficeTracker" /f
```

### Activar ejecución automática
```cmd
schtasks /create /tn "OfficeTracker" /tr "powershell -ExecutionPolicy Bypass -File C:\ruta\completa\check_wifi.ps1" /sc minute /mo 30 /f
```

---

## 🔧 Resolución de Problemas

### Error: "execution of scripts is disabled"
Abrir PowerShell como Administrador y ejecutar:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### El script no detecta la red
Verificar gateway actual:
```cmd
ipconfig | findstr "Gateway"
```

### Python no encontrado
1. Instalar Python desde https://www.python.org/downloads/
2. Durante instalación, marcar "Add Python to PATH"

---

## 📝 Archivos

- `check_wifi.ps1` - Script de detección (PowerShell)
- `setup.bat` - Instalador
- `view_report.bat` - Lanzador del dashboard
- `report.html` - Dashboard web dinámico
- `attendance.json` - Base de datos
- `tracker.log` - Historial
- `Boehringer_Logo_RGB_Accent-Green.svg` - Logo

---

## ✨ Características

- ✅ Compatible con Windows 10/11
- ✅ Task Scheduler para ejecución automática
- ✅ Notificaciones nativas de Windows
- ✅ Dashboard web idéntico a la versión macOS
- ✅ API de feriados argentinos
- ✅ Sin dependencias externas (solo Python para dashboard)

---

## 🔒 Privacidad

- ✅ Todos los datos se almacenan localmente
- ✅ No envía información a servidores externos
- ✅ Solo consulta API pública de feriados
