import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from inventoryApp import inventoryApp, db

inventoryApp.config.from_object(os.environ["APP_SETTINGS"])

migrate = Migrate(inventoryApp, db)
manager = Manager(inventoryApp)

manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
