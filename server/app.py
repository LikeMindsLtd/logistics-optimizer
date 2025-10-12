from . import create_app # Import the factory function

# Call the factory to create the application instance
app = create_app() 

if __name__ == '__main__':
    # When running locally, Flask uses the development server
    app.run(debug=True, port=5000)