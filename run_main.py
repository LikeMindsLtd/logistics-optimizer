from main_server import create_app
from main_server import db

app = create_app()

# with app.app_context():   **Tables already created hence running this adds uneccessary overhead**
#     db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')