#!/bin/bash
# Database Restore Script for Render PostgreSQL
# This script restores a database from a SQL dump file
#
# Usage:
#   ./scripts/restore_database.sh <backup_file>
#
# Environment Variables Required:
#   DATABASE_URL - PostgreSQL connection string for the NEW database

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Example:"
    echo "  $0 backups/backstock_backup_20250116_120000.sql"
    echo "  $0 backups/backstock_backup_20250116_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Error: DATABASE_URL environment variable is not set${NC}"
    echo "Please set DATABASE_URL to your NEW PostgreSQL connection string"
    exit 1
fi

echo -e "${YELLOW}Database Restore Process${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Backup file: $BACKUP_FILE"
echo "Target database: $DATABASE_URL"
echo ""

# Warning prompt
echo -e "${YELLOW}⚠ WARNING: This will OVERWRITE the target database!${NC}"
read -p "Are you sure you want to continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

# Handle compressed files
TEMP_FILE=""
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo -e "${YELLOW}Decompressing backup file...${NC}"
    TEMP_FILE="/tmp/restore_temp_$$.sql"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    RESTORE_FILE="$TEMP_FILE"
else
    RESTORE_FILE="$BACKUP_FILE"
fi

echo -e "${YELLOW}Starting database restore...${NC}"

# Restore the database
psql "$DATABASE_URL" < "$RESTORE_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database restore completed successfully!${NC}"
else
    echo -e "${RED}✗ Database restore failed${NC}"
    [ -n "$TEMP_FILE" ] && rm -f "$TEMP_FILE"
    exit 1
fi

# Clean up temporary file
[ -n "$TEMP_FILE" ] && rm -f "$TEMP_FILE"

echo ""
echo -e "${GREEN}Restore process complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Verify data with: psql \$DATABASE_URL -c 'SELECT COUNT(*) FROM grocery_items;'"
echo "  2. Run migrations if needed: python manage.py db upgrade"
