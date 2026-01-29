# Office Attendance Tracker

Sistema de tracking automático de asistencia a oficina basado en detección de red WiFi.

---

## 🚀 Instalación Rápida

### 1. Descargar o clonar el proyecto
Coloca los archivos en cualquier carpeta de tu computadora (por ejemplo: `~/office-tracker`)

### 2. Ejecutar setup
```bash
cd ~/office-tracker  # O la carpeta donde colocaste los archivos
./setup.sh
```

El script de setup hará:
- ✅ Configurar permisos de ejecución
- ✅ Crear la base de datos
- ✅ Verificar la conexión de red
- ✅ Probar el funcionamiento
- ✅ Opcionalmente instalar ejecución automática

### 3. ¡Listo!
El sistema detectará automáticamente cuando estés conectado a la red de oficina (BI-Mobile) y registrará tu asistencia.

---

## 📊 Ver Estadísticas

Ejecuta
```bash
./show_attendance.sh
```

Muestra:
- 📅 Días totales de asistencia
- 📆 Días del mes actual
- 📈 Últimas asistencias registradas

---

## 🔧 Resolución de Problemas

### El script no detecta la oficina

**Verificar el gateway actual:**
```bash
route -n get default | grep gateway
```

**Si el gateway es diferente a `10.15.16.1`:**
1. Edita [check_wifi.sh](check_wifi.sh)
2. Cambia la línea:
   ```bash
   OFFICE_GATEWAY="TU_GATEWAY_AQUI"
   ```

### Ver logs de detección

```bash
cat tracker.log
```

### Probar manualmente

```bash
./check_wifi.sh
cat attendance.json
```

---

## 🔍 Cómo Funciona

1. **Detección automática**: El script verifica el gateway de red cada 30 minutos
2. **Identificación**: Busca el gateway de la oficina (10.15.16.1 para BI-Mobile)
3. **Registro único**: Guarda solo una entrada por día en `attendance.json`
4. **Notificación**: Te avisa cuando registra tu asistencia

---

## ⚙️ Configuración Avanzada

### Desactivar ejecución automática

```bash
launchctl unload ~/Library/LaunchAgents/com.office-tracker.plist
```

### Activar ejecución automática

```bash
launchctl load ~/Library/LaunchAgents/com.office-tracker.plist
```

### Cambiar frecuencia de verificación

Edita el archivo plist en `~/Library/LaunchAgents/com.office-tracker.plist`:
```xml
<key>StartInterval</key>
<integer>1800</integer>  <!-- 1800 = 30 minutos -->
```

Luego recarga:
```bash
launchctl unload ~/Library/LaunchAgents/com.office-tracker.plist
launchctl load ~/Library/LaunchAgents/com.office-tracker.plist
```

### Detectar múltiples redes de oficina

Edita [check_wifi.sh](check_wifi.sh) línea 37:
```bash
if [ "$CURRENT_GATEWAY" = "10.15.16.1" ] || [ "$CURRENT_GATEWAY" = "OTRO_GATEWAY" ]; then
```

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
| `com.fuenmayo.office-tracker.plist` | Plantilla de configuración |

---

## 💡 Uso en Nueva Computadora

1. Copia la carpeta completa a la nueva Mac
2. Ejecuta `./setup.sh`
3. ¡Listo!
