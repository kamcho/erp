#!/bin/bash

# Linux Shell Backup Automation Script
# Automatically detects the project directory relative to the script location

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Move to the project directory
cd "$PROJECT_DIR"

# Detect Python interpreter (prefer virtualenv if exists)
PYTHON_PATH="python3"
if [ -f "$PROJECT_DIR/venv/bin/python" ]; then
    PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
elif [ -f "$PROJECT_DIR/env/bin/python" ]; then
    PYTHON_PATH="$PROJECT_DIR/env/bin/python"
fi

echo "Starting database backup task at $(date)..."
echo "Using python: $PYTHON_PATH"
echo "Project directory: $PROJECT_DIR"

# Run the Django management command
$PYTHON_PATH manage.py backup_db

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Backup process completed successfully."
else
    echo "Error: Backup process failed with exit code $EXIT_CODE" >&2
    exit $EXIT_CODE
fi
