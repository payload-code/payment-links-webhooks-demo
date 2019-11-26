from flask import Flask, request
app = Flask(__name__)
from routes import routes

app.register_blueprint(routes)

if __name__ == '__main__':
    # app.debug = True
    # Default port is 5000
    app.run(host='0.0.0.0')
