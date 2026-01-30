#!/bin/bash

# Office Attendance Tracker - WiFi Detection Script
# Detecta si estás conectado a la red de oficina y registra la asistencia
# 
# Método: Detecta el gateway de la red (10.15.16.1 = oficina BI-Mobile)

# Gateway de la oficina (BI-Mobile)
OFFICE_GATEWAY="10.15.16.1"

# Obtener el directorio donde está este script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATA_DIR="$SCRIPT_DIR"
DATA_FILE="$DATA_DIR/attendance.json"
LOG_FILE="$DATA_DIR/tracker.log"

# Función para logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Asegurar que el directorio existe
mkdir -p "$DATA_DIR"

# Crear archivo JSON si no existe
if [ ! -f "$DATA_FILE" ]; then
    echo '{"dates":[]}' > "$DATA_FILE"
    log "Archivo de asistencia creado"
fi

# Obtener el gateway actual
CURRENT_GATEWAY=$(route -n get default 2>/dev/null | grep gateway | awk '{print $2}')

log "Gateway detectado: '$CURRENT_GATEWAY'"

# Verificar si estamos en la red de oficina
if [ "$CURRENT_GATEWAY" = "$OFFICE_GATEWAY" ]; then
    TODAY=$(date '+%Y-%m-%d')
    
    # Verificar si ya se registró hoy
    if grep -q "\"$TODAY\"" "$DATA_FILE"; then
        log "Ya registrado hoy ($TODAY)"
    else
        # Agregar la fecha al JSON
        CURRENT_DATES=$(cat "$DATA_FILE" | sed 's/.*\[//' | sed 's/\].*//')
        
        if [ -z "$CURRENT_DATES" ]; then
            NEW_DATES="\"$TODAY\""
        else
            NEW_DATES="\"$TODAY\",$CURRENT_DATES"
        fi
        
        echo "{\"dates\":[$NEW_DATES]}" > "$DATA_FILE"
        log "✓ Asistencia registrada: $TODAY"
        
        # Notificación
        osascript -e 'display notification "Asistencia registrada para hoy" with title "Office Tracker" sound name "Glass"' 2>/dev/null
    fi
else
    log "No conectado a oficina (gateway: $CURRENT_GATEWAY)"
fi
