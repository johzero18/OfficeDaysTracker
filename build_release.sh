#!/bin/bash

# Script para compilar OfficeDaysTracker para distribución

set -e

# Nombre del proyecto en Xcode
PROJECT_NAME="ControlOficina"
# Nombre final para distribución
DIST_NAME="OfficeDaysTracker"
ARCHIVE_PATH="build/${PROJECT_NAME}.xcarchive"
EXPORT_PATH="build/export"

echo "🔨 Compilando ${PROJECT_NAME}..."

# Limpiar builds anteriores
rm -rf build
mkdir -p build

# Compilar el proyecto
xcodebuild -scheme ${PROJECT_NAME} \
    -configuration Release \
    -archivePath "${ARCHIVE_PATH}" \
    archive

# Exportar la app
xcodebuild -exportArchive \
    -archivePath "${ARCHIVE_PATH}" \
    -exportPath "${EXPORT_PATH}" \
    -exportOptionsPlist exportOptions.plist

echo "✅ Build completado: ${EXPORT_PATH}/${PROJECT_NAME}.app"

# Renombrar la app para distribución
mv "${EXPORT_PATH}/${PROJECT_NAME}.app" "${EXPORT_PATH}/${DIST_NAME}.app"

# Crear archivo ZIP para distribución
cd "${EXPORT_PATH}"
zip -r "../${DIST_NAME}.zip" "${DIST_NAME}.app"
cd - > /dev/null

echo "📦 Archivo ZIP creado: build/${DIST_NAME}.zip"
echo ""
echo "🔐 SHA256:"
shasum -a 256 "build/${DIST_NAME}.zip"
