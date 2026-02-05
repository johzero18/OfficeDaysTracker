#!/bin/bash

# Script para crear un instalador DMG de Control Oficina
# Autor: Generado automáticamente
# Fecha: $(date)

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Control Oficina - Creador de Instalador${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Variables
APP_NAME="ControlOficina"
APP_DISPLAY_NAME="OfficeDaysTracker"
SCHEME="ControlOficina"
PROJECT="ControlOficina.xcodeproj"
BUILD_DIR="build"
DMG_NAME="OfficeDaysTracker-Installer.dmg"
DMG_TEMP_NAME="OfficeDaysTracker-temp.dmg"
VOLUME_NAME="Office Days Tracker"

# Limpiar builds anteriores
echo -e "${YELLOW}Limpiando builds anteriores...${NC}"
rm -rf "$BUILD_DIR"
rm -f "$DMG_NAME"
rm -f "$DMG_TEMP_NAME"

# Compilar la aplicación en modo Release para ambas arquitecturas (Universal Binary)
echo -e "${YELLOW}Compilando aplicación en modo Release para Intel y Apple Silicon...${NC}"
xcodebuild -project "$PROJECT" \
    -scheme "$SCHEME" \
    -configuration Release \
    -derivedDataPath "$BUILD_DIR" \
    -arch x86_64 -arch arm64 \
    ONLY_ACTIVE_ARCH=NO \
    clean build

# Verificar que la aplicación se compiló correctamente
APP_PATH="$BUILD_DIR/Build/Products/Release/$APP_NAME.app"
if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}Error: No se encontró la aplicación compilada en $APP_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Aplicación compilada correctamente${NC}\n"

# Crear directorio temporal para el DMG
echo -e "${YELLOW}Creando estructura del instalador...${NC}"
DMG_DIR="$BUILD_DIR/dmg"
mkdir -p "$DMG_DIR"

# Copiar la aplicación al directorio temporal
cp -R "$APP_PATH" "$DMG_DIR/"

# Renombrar la app para el usuario
mv "$DMG_DIR/$APP_NAME.app" "$DMG_DIR/$APP_DISPLAY_NAME.app"

# Crear un enlace a la carpeta Aplicaciones
ln -s /Applications "$DMG_DIR/Applications"

# Copiar el ícono de la carpeta Applications del sistema para hacerlo visible
cp -R /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ToolbarApplicationsFolderIcon.icns "$DMG_DIR/.VolumeIcon.icns" 2>/dev/null || true

# Crear archivo README con instrucciones
cat > "$DMG_DIR/INSTRUCCIONES.txt" << 'EOF'
OFFICE DAYS TRACKER - INSTALACIÓN
==================================

Para instalar Office Days Tracker:

1. Arrastra el icono "OfficeDaysTracker" a la carpeta "Applications"
2. Abre la carpeta Aplicaciones (Applications)
3. Busca "OfficeDaysTracker" y ábrelo
4. La primera vez, macOS puede pedir permiso. Si aparece un mensaje de seguridad:
   - Ve a Preferencias del Sistema > Privacidad y Seguridad
   - Haz clic en "Abrir de todas formas"
5. Una vez abierto, verás el icono en la barra de menú superior
6. Haz clic en el icono para usar la aplicación

NOTA: La aplicación NO aparecerá en el Dock. Solo verás un icono 
en la barra de menú superior (junto al reloj, WiFi, etc.)

Para desinstalar:
- Simplemente arrastra OfficeDaysTracker.app desde la carpeta Applications a la Papelera

¡Listo!
EOF

echo -e "${GREEN}✓ Estructura creada${NC}\n"

# Crear el DMG
echo -e "${YELLOW}Creando imagen de disco DMG...${NC}"

# Crear DMG temporal
hdiutil create -srcfolder "$DMG_DIR" \
    -volname "$VOLUME_NAME" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDRW \
    -size 100m \
    "$DMG_TEMP_NAME"

# Montar el DMG temporal
MOUNT_DIR=$(hdiutil attach "$DMG_TEMP_NAME" | grep -o '/Volumes/.*$')
echo "DMG montado en: $MOUNT_DIR"

# Configurar la apariencia del DMG (opcional, requiere AppleScript)
if [ -d "$MOUNT_DIR" ]; then
    # Esperar un momento para que se monte completamente
    sleep 2
    
    # Configurar la vista del Finder
    osascript <<EOF
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 900, 450}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 72
        set position of item "OfficeDaysTracker.app" of container window to {120, 120}
        set position of item "Applications" of container window to {380, 120}
        set position of item "INSTRUCCIONES.txt" of container window to {250, 280}
        
        -- Hacer visible el enlace de Applications
        try
            set the extension hidden of item "Applications" to false
        end try
        
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
EOF
    
    # Asignar ícono personalizado al enlace de Applications
    if [ -f "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ToolbarApplicationsFolderIcon.icns" ]; then
        # Usar el comando SetFile para hacer el enlace más visible
        /usr/bin/SetFile -a E "$MOUNT_DIR/Applications" 2>/dev/null || true
    fi
    
    # Sincronizar y desmontar
    sync
    sleep 2
fi

# Desmontar el DMG temporal
hdiutil detach "$MOUNT_DIR" || true
sleep 1

# Convertir a DMG comprimido final
echo -e "${YELLOW}Comprimiendo instalador...${NC}"
hdiutil convert "$DMG_TEMP_NAME" \
    -format UDZO \
    -imagekey zlib-level=9 \
    -o "$DMG_NAME"

# Limpiar archivos temporales
rm -f "$DMG_TEMP_NAME"
rm -rf "$DMG_DIR"

# Obtener tamaño del archivo
DMG_SIZE=$(du -h "$DMG_NAME" | cut -f1)

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ INSTALADOR CREADO EXITOSAMENTE${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Archivo: ${YELLOW}$DMG_NAME${NC}"
echo -e "Tamaño: ${YELLOW}$DMG_SIZE${NC}"
echo -e "Ubicación: ${YELLOW}$(pwd)/$DMG_NAME${NC}\n"
echo -e "${GREEN}Puedes distribuir este archivo .dmg a otros usuarios.${NC}"
echo -e "${GREEN}Al abrirlo, solo necesitan arrastrar la app a Aplicaciones.${NC}\n"
