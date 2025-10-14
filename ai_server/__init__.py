from flask import Flask
from ai_server.api.ai_routes import bp as ai_bp

def create_app():
    app = Flask("ai_server")

    # Optional: Load configuration if needed
    app.config.from_object('ai_server.config')

    # Register routes
    app.register_blueprint(ai_bp)

    return app
