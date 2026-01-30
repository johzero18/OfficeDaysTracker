#!/bin/bash

# Office Attendance Tracker - Visualization Script
# Shows office attendance statistics

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATA_DIR="$SCRIPT_DIR"
DATA_FILE="$DATA_DIR/attendance.json"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Argentina holidays 2026
HOLIDAYS_2026=(
    "2026-01-01"  # New Year
    "2026-02-16"  # Carnival Monday
    "2026-02-17"  # Carnival Tuesday
    "2026-03-24"  # Memorial Day
    "2026-04-02"  # Malvinas Day
    "2026-04-03"  # Good Friday
    "2026-05-01"  # Labor Day
    "2026-05-25"  # May Revolution
    "2026-06-15"  # Flag Day
    "2026-06-20"  # Güemes Day
    "2026-07-09"  # Independence Day
    "2026-08-17"  # San Martín Day
    "2026-10-12"  # Diversity Day
    "2026-11-23"  # Sovereignty Day
    "2026-12-08"  # Immaculate Conception
    "2026-12-25"  # Christmas
)

# Check if file exists
if [ ! -f "$DATA_FILE" ]; then
    echo -e "${YELLOW}⚠ No attendance data yet.${NC}"
    echo "File will be created automatically when you connect to office network."
    exit 0
fi

# Extract dates from JSON
DATES=$(cat "$DATA_FILE" | sed 's/.*\[//' | sed 's/\].*//' | tr ',' '\n' | tr -d '"' | tr -d ' ' | sort)

if [ -z "$DATES" ]; then
    echo -e "${YELLOW}⚠ No dates registered yet.${NC}"
    exit 0
fi

# Count total days
TOTAL_DAYS=$(echo "$DATES" | wc -l | tr -d ' ')

# Get current month and year
CURRENT_YEAR=$(date '+%Y')
CURRENT_MONTH=$(date '+%m')
CURRENT_MONTH_NAME=$(date '+%B')

# Count days in current month
CURRENT_MONTH_DAYS=$(echo "$DATES" | grep "^$CURRENT_YEAR-$CURRENT_MONTH" | wc -l | tr -d ' ')

# Get last date
LAST_DATE=$(echo "$DATES" | tail -1)

# Calculate remaining workdays in current month
CURRENT_DAY=$(date '+%d')
DAYS_IN_MONTH=$(date -v1d -v+1m -v-1d '+%d')
REMAINING_WORKDAYS=0

for ((day=$CURRENT_DAY+1; day<=DAYS_IN_MONTH; day++)); do
    CHECK_DATE=$(printf "%s-%s-%02d" "$CURRENT_YEAR" "$CURRENT_MONTH" "$day")
    DAY_OF_WEEK=$(date -j -f "%Y-%m-%d" "$CHECK_DATE" "+%u" 2>/dev/null)
    
    # Check if it's a weekday (1-5 = Mon-Fri)
    if [ "$DAY_OF_WEEK" -ge 1 ] && [ "$DAY_OF_WEEK" -le 5 ]; then
        # Check if it's not a holiday
        IS_HOLIDAY=0
        for HOLIDAY in "${HOLIDAYS_2026[@]}"; do
            if [ "$CHECK_DATE" = "$HOLIDAY" ]; then
                IS_HOLIDAY=1
                break
            fi
        done
        
        if [ "$IS_HOLIDAY" -eq 0 ]; then
            REMAINING_WORKDAYS=$((REMAINING_WORKDAYS + 1))
        fi
    fi
done

# Header
echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║       🏢 OFFICE ATTENDANCE TRACKER               ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Main statistics
echo -e "${BOLD}📊 STATISTICS${NC}"
echo -e "────────────────────────────────────────────────────"
echo -e "${GREEN}✓ Total office days:${NC} ${BOLD}$TOTAL_DAYS days${NC}"
echo -e "${GREEN}✓ This month ($CURRENT_MONTH_NAME):${NC} ${BOLD}$CURRENT_MONTH_DAYS days${NC}"
echo -e "${GREEN}✓ Last record:${NC} $LAST_DATE"
echo -e "${CYAN}✓ Workdays remaining in month:${NC} ${BOLD}$REMAINING_WORKDAYS days${NC}"
echo ""

# Monthly summary
echo -e "${BOLD}📅 MONTHLY SUMMARY${NC}"
echo -e "────────────────────────────────────────────────────"

# Get all unique year-months
MONTHS=$(echo "$DATES" | sed 's/-[0-9]*$//' | sort -u)

for MONTH in $MONTHS; do
    MONTH_COUNT=$(echo "$DATES" | grep "^$MONTH" | wc -l | tr -d ' ')
    YEAR_PART=$(echo "$MONTH" | cut -d'-' -f1)
    MONTH_PART=$(echo "$MONTH" | cut -d'-' -f2)
    
    # Convert month number to name
    case $MONTH_PART in
        01) MONTH_NAME="January";;
        02) MONTH_NAME="February";;
        03) MONTH_NAME="March";;
        04) MONTH_NAME="April";;
        05) MONTH_NAME="May";;
        06) MONTH_NAME="June";;
        07) MONTH_NAME="July";;
        08) MONTH_NAME="August";;
        09) MONTH_NAME="September";;
        10) MONTH_NAME="October";;
        11) MONTH_NAME="November";;
        12) MONTH_NAME="December";;
    esac
    
    # Create visual bar
    BAR=""
    for ((i=0; i<MONTH_COUNT && i<20; i++)); do
        BAR="${BAR}█"
    done
    
    printf "${BLUE}%-15s${NC} ${GREEN}%s${NC} (%d days)\n" "$MONTH_NAME $YEAR_PART" "$BAR" "$MONTH_COUNT"
done

echo ""

# Show last 10 days
echo -e "${BOLD}🕐 LAST 10 DAYS REGISTERED${NC}"
echo -e "────────────────────────────────────────────────────"
echo "$DATES" | tail -10 | while read DATE; do
    # Get day of week
    if [ -n "$DATE" ]; then
        DAY_OF_WEEK=$(date -j -f "%Y-%m-%d" "$DATE" "+%A" 2>/dev/null)
        echo -e "  ${CYAN}•${NC} $DATE ($DAY_OF_WEEK)"
    fi
done

echo ""
echo -e "${BOLD}${CYAN}══════════════════════════════════════════════════${NC}"
echo ""
