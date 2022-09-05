from config import PORT, DEBUG
from dash.routes import app

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')