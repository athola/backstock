"""Shared database instance for the application.

This module provides a single SQLAlchemy instance that is shared across
the application to avoid the "multiple SQLAlchemy instances" error.
"""

from flask_sqlalchemy import SQLAlchemy

# Create db instance without binding to an app yet
# The app will be bound in connexion_app.py using db.init_app(app)
db = SQLAlchemy()
