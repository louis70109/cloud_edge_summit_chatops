from flask import Flask, request
from werkzeug.exceptions import RequestTimeout
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Summary, Counter
import random
import time

app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

REQUESTS = Counter('server_requests_total', 'Total number of requests to this webserver')
c = Counter('my_requests_total', 'HTTP Failures', ['method', 'endpoint'])


@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)


@app.route("/items", methods=['GET'])
def get_item():
    process_request(random.random())
    REQUESTS.inc()
    return [{'id': 1, 'name': 'Book', 'desc': 'I am a book'},
            {'id': 2, 'name': 'Coffee', 'desc': 'Good to drink'}]


@app.route("/items", methods=['POST'])
def post_item():
    if request.args.get('name'):
        c.labels('post', '/items').inc()
        # name too long than SQL column
        raise RequestTimeout()
    REQUESTS.inc()
    return {'id': 1, 'name': 'Book', 'desc': 'I am a book'}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=31110, debug=True)
    # app.run(host='0.0.0.0', port=8000, debug=True)
