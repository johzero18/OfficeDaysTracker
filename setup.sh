#!/bin/bash

# Office Tracker - Setup Automático
# Configura el sistema de tracking de asistencia

echo "🏢 OFFICE TRACKER - SETUP"
echo "========================================"
echo ""

# Obtener el directorio donde está este script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📂 Directorio de instalación: $SCRIPT_DIR"
echo ""

# 1. Dar permisos
echo "1️⃣  Configurando permisos..."
chmod +x "$SCRIPT_DIR/check_wifi.sh"
chmod +x "$SCRIPT_DIR/show_attendance.sh"
echo "   ✅ Permisos configurados"
echo ""

# 2. Crear attendance.json si no existe
if [ ! -f "$SCRIPT_DIR/attendance.json" ]; then
    echo "2️⃣  Creando base de datos..."
    echo '{"dates":[]}' > "$SCRIPT_DIR/attendance.json"
    echo "   ✅ attendance.json creado"
else
    echo "2️⃣  Base de datos ya existe"
    DATES_COUNT=$(grep -o '"[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}"' "$SCRIPT_DIR/attendance.json" | wc -l | tr -d ' ')
    echo "   Fechas registradas: $DATES_COUNT"
fi
echo ""

# 3. Verificar red
echo "3️⃣  Verificando conexión de red..."
CURRENT_GATEWAY=$(route -n get default 2>/dev/null | grep gateway | awk '{print $2}')

if [ -n "$CURRENT_GATEWAY" ]; then
    echo "   Gateway detectado: $CURRENT_GATEWAY"
    if [ "$CURRENT_GATEWAY" = "10.15.16.1" ]; then
        echo "   ✅ ¡Estás en la red de oficina!"
    else
        echo "   ⚠️  No estás en la red de oficina"
        echo "   💡 Cuando estés en BI-Mobile, el gateway debería ser 10.15.16.1"
        echo "   💡 Si es diferente, edita check_wifi.sh y cambia OFFICE_GATEWAY"
    fi
else
    echo "   ⚠️  No hay red detectada"
fi
echo ""

# 4. Probar script
echo "4️⃣  Probando script de detección..."
"$SCRIPT_DIR/check_wifi.sh"
if [ -f "$SCRIPT_DIR/tracker.log" ]; then
    echo "   Último log:"
    tail -1 "$SCRIPT_DIR/tracker.log" | sed 's/^/   /'
    echo "   ✅ Script funciona correctamente"
else
    echo "   ❌ No se generó el log"
fi
echo ""

# 5. Instalar LaunchAgent
echo "5️⃣  ¿Instalar ejecución automática al inicio? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    # Crear plist personalizado con la ruta correcta
    PLIST_FILE="$HOME/Library/LaunchAgents/com.office-tracker.plist"
    
    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.office-tracker</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$SCRIPT_DIR/check_wifi.sh</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>StartInterval</key>
    <integer>1800</integer>
    
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/error.log</string>
    
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF
    
    launchctl load "$PLIST_FILE" 2>/dev/null
    echo "   ✅ LaunchAgent instalado y activo"
    echo "   El sistema se ejecutará automáticamente cada 30 minutos"
else
    echo "   ⏭️  Saltando instalación automática"
    echo "   💡 Para instalar después, ejecuta nuevamente este script"
fi
echo ""

# 6. Resumen
echo "========================================"
echo "✅ SETUP COMPLETADO"
echo ""
echo "📊 Para ver estadísticas:"
echo "   $SCRIPT_DIR/show_attendance.sh"
echo ""
echo "📝 Archivos:"
echo "   • check_wifi.sh - Script principal"
echo "   • attendance.json - Base de datos"
echo "   • tracker.log - Historial de detecciones"
echo ""
echo "📖 Más info: $SCRIPT_DIR/README.md"
echo "========================================"
