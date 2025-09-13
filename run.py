from app import flask_app

if __name__ == '__main__':
    # Note: For production, use a proper WSGI server like Gunicorn or uWSGI
    flask_app.run(host='0.0.0.0', port=8080, debug=True)