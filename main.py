# This file is for running the application
# Import app after it's fully initialized to avoid circular imports
if __name__ == '__main__':
    from app import app
    app.run(host="0.0.0.0", port=5000, debug=True)
