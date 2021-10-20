from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Summary, Gauge, Counter
import random
import time


app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

REQUESTS = Counter('server_requests_total', 'Total number of requests to this webserver')
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)

@app.route("/", methods=['GET'])
def hello():
    process_request(random.random())
    REQUESTS.inc()
    return "Hello Cloud Edge"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=31110, debug=True)
    # app.run(host='0.0.0.0', port=8000, debug=True)