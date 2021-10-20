from flask import Flask

from flask import json
import requests  
import json
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route("/", methods=['GET'])
def hello():
    return "World"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=31110, debug=True)
    # app.run(host='0.0.0.0', port=8000, debug=True)