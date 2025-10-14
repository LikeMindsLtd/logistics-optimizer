from flask import Flask
from .models import db
from dotenv import load_dotenv
from .config import DevConfig
from flask_cors import CORS

load_dotenv()

def create_app(config_class=DevConfig):

    app = Flask("main-server")
    app.config.from_object(config_class)
    CORS(app, origins="http://localhost:5173")
    db.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    return app
