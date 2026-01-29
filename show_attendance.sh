#!/bin/bash

# Office Attendance Tracker - Visualization Script
# Muestra estadísticas de asistencia a la oficina

DATA_DIR="$HOME/Sites/control-oficina"
DATA_FILE="$DATA_DIR/attendance.json"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Verificar si existe el archivo
if [ ! -f "$DATA_FILE" ]; then
    echo -e "${YELLOW}⚠ No hay datos de asistencia aún.${NC}"
    echo "El archivo se creará automáticamente cuando te conectes a la red de oficina."
    exit 0
fi

# Extraer las fechas del JSON
DATES=$(cat "$DATA_FILE" | sed 's/.*\[//' | sed 's/\].*//' | tr ',' '\n' | tr -d '"' | tr -d ' ' | sort)

if [ -z "$DATES" ]; then
    echo -e "${YELLOW}⚠ No hay fechas registradas aún.${NC}"
    exit 0
fi

# Contar días totales
TOTAL_DAYS=$(echo "$DATES" | wc -l | tr -d ' ')

# Obtener mes y año actual
CURRENT_YEAR=$(date '+%Y')
CURRENT_MONTH=$(date '+%m')
CURRENT_MONTH_NAME=$(date '+%B')

# Contar días del mes actual
CURRENT_MONTH_DAYS=$(echo "$DATES" | grep "^$CURRENT_YEAR-$CURRENT_MONTH" | wc -l | tr -d ' ')

# Obtener primera y última fecha
FIRST_DATE=$(echo "$DATES" | head -1)
LAST_DATE=$(echo "$DATES" | tail -1)

# Header
echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║       🏢 OFFICE ATTENDANCE TRACKER               ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Estadísticas principales
echo -e "${BOLD}📊 ESTADÍSTICAS${NC}"
echo -e "────────────────────────────────────────────────────"
echo -e "${GREEN}✓ Total de días en oficina:${NC} ${BOLD}$TOTAL_DAYS días${NC}"
echo -e "${GREEN}✓ Este mes ($CURRENT_MONTH_NAME):${NC} ${BOLD}$CURRENT_MONTH_DAYS días${NC}"
echo -e "${GREEN}✓ Primer registro:${NC} $FIRST_DATE"
echo -e "${GREEN}✓ Último registro:${NC} $LAST_DATE"
echo ""

# Mostrar resumen por mes
echo -e "${BOLD}📅 RESUMEN POR MES${NC}"
echo -e "────────────────────────────────────────────────────"

# Obtener todos los años-meses únicos
MONTHS=$(echo "$DATES" | sed 's/-[0-9]*$//' | sort -u)

for MONTH in $MONTHS; do
    MONTH_COUNT=$(echo "$DATES" | grep "^$MONTH" | wc -l | tr -d ' ')
    YEAR_PART=$(echo "$MONTH" | cut -d'-' -f1)
    MONTH_PART=$(echo "$MONTH" | cut -d'-' -f2)
    
    # Convertir número de mes a nombre
    case $MONTH_PART in
        01) MONTH_NAME="Enero";;
        02) MONTH_NAME="Febrero";;
        03) MONTH_NAME="Marzo";;
        04) MONTH_NAME="Abril";;
        05) MONTH_NAME="Mayo";;
        06) MONTH_NAME="Junio";;
        07) MONTH_NAME="Julio";;
        08) MONTH_NAME="Agosto";;
        09) MONTH_NAME="Septiembre";;
        10) MONTH_NAME="Octubre";;
        11) MONTH_NAME="Noviembre";;
        12) MONTH_NAME="Diciembre";;
    esac
    
    # Crear barra visual
    BAR=""
    for ((i=0; i<MONTH_COUNT && i<20; i++)); do
        BAR="${BAR}█"
    done
    
    printf "${BLUE}%-15s${NC} ${GREEN}%s${NC} (%d días)\n" "$MONTH_NAME $YEAR_PART" "$BAR" "$MONTH_COUNT"
done

echo ""

# Mostrar últimos 10 días
echo -e "${BOLD}🕐 ÚLTIMOS 10 DÍAS REGISTRADOS${NC}"
echo -e "────────────────────────────────────────────────────"
echo "$DATES" | tail -10 | while read DATE; do
    # Obtener día de la semana
    if [ -n "$DATE" ]; then
        DAY_OF_WEEK=$(date -j -f "%Y-%m-%d" "$DATE" "+%A" 2>/dev/null)
        echo -e "  ${CYAN}•${NC} $DATE ($DAY_OF_WEEK)"
    fi
done

echo ""
echo -e "${BOLD}${CYAN}══════════════════════════════════════════════════${NC}"
echo ""
