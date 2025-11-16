#!/bin/bash
# Database Backup Script for Render PostgreSQL
# This script backs up the database to a timestamped SQL dump file
#
# Usage:
#   ./scripts/backup_database.sh [output_directory]
#
# Environment Variables Required:
#   DATABASE_URL - PostgreSQL connection string

set -e  # Exit on error

# Configuration
BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backstock_backup_${TIMESTAMP}.sql"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Error: DATABASE_URL environment variable is not set${NC}"
    echo "Please set DATABASE_URL to your PostgreSQL connection string"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}Starting database backup...${NC}"
echo "Backup file: $BACKUP_FILE"

# Perform backup using pg_dump
# The DATABASE_URL format is: postgresql://user:password@host:port/dbname
pg_dump "$DATABASE_URL" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Get file size
    FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✓ Backup completed successfully!${NC}"
    echo "  File: $BACKUP_FILE"
    echo "  Size: $FILE_SIZE"
    echo ""
    echo "To restore this backup, run:"
    echo "  ./scripts/restore_database.sh $BACKUP_FILE"
else
    echo -e "${RED}✗ Backup failed${NC}"
    exit 1
fi

# Optional: Compress the backup
if command -v gzip &> /dev/null; then
    echo -e "${YELLOW}Compressing backup...${NC}"
    gzip "$BACKUP_FILE"
    COMPRESSED_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    echo -e "${GREEN}✓ Compressed to ${BACKUP_FILE}.gz (${COMPRESSED_SIZE})${NC}"
fi

# Clean up old backups (keep last 5)
echo -e "${YELLOW}Cleaning up old backups...${NC}"
cd "$BACKUP_DIR"
ls -t backstock_backup_*.sql* 2>/dev/null | tail -n +6 | xargs -r rm
echo -e "${GREEN}✓ Cleanup complete${NC}"

echo ""
echo -e "${GREEN}Backup process complete!${NC}"
