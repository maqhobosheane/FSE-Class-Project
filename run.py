import os
from app import flask_app

if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 8080))
    # Note: For production, use a proper WSGI server like Gunicorn or uWSGI
    flask_app.run(host='0.0.0.0', port=port, debug=False)