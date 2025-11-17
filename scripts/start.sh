#!/bin/bash
# Startup script for Render deployment (free tier)
# This runs database migrations before starting the application server

set -e  # Exit immediately if any command fails

echo "========================================="
echo "Starting PyBackstock Deployment"
echo "========================================="

# Run database migrations
echo "Running database migrations..."
python -c "
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up app configuration
os.environ.setdefault('APP_SETTINGS', 'src.pybackstock.config.ProductionConfig')

from flask_migrate import upgrade as flask_migrate_upgrade
from src.pybackstock import app, db
from flask_migrate import Migrate

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Run migrations
with app.app_context():
    try:
        flask_migrate_upgrade()
        print('✓ Database migrations completed successfully')
    except Exception as e:
        print(f'✗ Migration failed: {e}', file=sys.stderr)
        sys.exit(1)
"

echo "Migrations complete. Starting Gunicorn..."
echo "========================================="

# Start Gunicorn
exec gunicorn 'src.pybackstock.app:app' --bind 0.0.0.0:$PORT
