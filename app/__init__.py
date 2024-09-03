from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize the database object
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    print('call create app')

    # Load configurations
    app.config.from_object('instance.config.Config')

    # Initialize the database with the app
    db.init_app(app)
    print(app)
    # Initialize Flask-Migrate with the app and the database
    migrate = Migrate(app, db)

    # Import and register blueprints after initializing db and migrate
    from .routes import main
    from .auth import auth_blueprint

    app.register_blueprint(main)
    app.register_blueprint(auth_blueprint)

    return app
