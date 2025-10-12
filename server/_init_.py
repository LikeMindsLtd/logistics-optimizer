# server/_init_.py

from flask import Flask
from .models import db 

def create_app():
    app = Flask(_name_)
    
    # Configure the Database URI 
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://appuser:strongpassword@localhost/logistics_db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database connection with the app
    db.init_app(app)

    # Import and Register Blueprints (Routes)
    from . import routes 
    app.register_blueprint(routes.bp) 
    
    return app