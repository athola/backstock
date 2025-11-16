"""Management script for the pybackstock application."""

import os

from flask_migrate import Migrate

from src.pybackstock import app, db

# Configure the app
app.config.from_object(os.environ.get("APP_SETTINGS", "src.pybackstock.config.DevelopmentConfig"))

# Initialize Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run()
