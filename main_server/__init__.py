import os
from flask import Flask
from .models import db
from dotenv import load_dotenv
from .config import DevConfig

load_dotenv()

def create_app(config_class=DevConfig):

    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    return app
