#!/bin/bash

# Configuration
# Automatically detect the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
FILE_NAME="excel_db_backup_$DATE.sql.gz"

# Move to the project directory so we can find the .env file
cd $PROJECT_DIR

# Load environment variables (to get DB credentials)
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found at $PROJECT_DIR/.env"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Perform the backup using mysqldump
# It uses environment variables loaded from .env
mysqldump -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE | gzip > $BACKUP_DIR/$FILE_NAME

# Keep only the last 30 days of backups to prevent disk from filling up
find $BACKUP_DIR -type f -mtime +30 -name "*.sql.gz" -delete

echo "Backup completed successfully: $BACKUP_DIR/$FILE_NAME"
