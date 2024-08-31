from flask import Flask
from .routes import main
from .auth import auth_blueprint

def create_app():
    app = Flask(__name__)
    print('call create app')
    # Load configurations
    app.config.from_object('instance.config.Config')

    # Register Blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth_blueprint)

    # Initialize other components
    # db.init_app(app) # if using a database

    return app