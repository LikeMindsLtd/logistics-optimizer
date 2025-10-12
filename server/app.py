# server/app.py

from . import create_app # Import the factory function

# Call the factory to create the application instance
app = create_app() 

if _name_ == '_main_':
    # When running locally, Flask uses the development server
    app.run(debug=True, port=5000)