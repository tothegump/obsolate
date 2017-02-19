# -*- coding:utf8 -*-
REQUEST_MAPPING = {
    'GET': {},
    'POST': {},
    'PUT': {},
    'DELETE': {},
}


class NotFound(Exception):
    pass


def find_matching_url(environ, start_response):
    request_method = environ.get('REQUEST_METHOD', 'GET')
    if request_method not in REQUEST_MAPPING:
        raise NotFound('not support method :(')
    path = environ.get('PATH_INFO', '')
    for url, method in REQUEST_MAPPING[request_method].items():
        if url == path:
            return method
    raise NotFound('Sorry, you got nothing!')


def not_found(environ, start_response):
    start_response(b'404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']


def handle_request(environ, start_response):
    try:
        callback = find_matching_url(environ, start_response)
    except NotFound:
        return not_found(environ, start_response)
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return callback()


def take_a_snap():
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8091, handle_request)
    print 'start listen localhost:8091...'
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print 'keyboard interrupt le..'
        srv.server_close()
        raise


# decorators
def get(url):

    def wrapped(func):

        def new(*args, **kwargs):
            return func(*args, **kwargs)
        # Register.
        REQUEST_MAPPING['GET'][url] = new
    return wrapped


def post(url):
    def wrapped(func):
        def new(*args, **kwargs):
            return func(*args, **kwargs)
        return new
    return wrapped


@get('/')
def index():
    return 'Indexed'


@get('/hello')
def greeting():
    return 'hello world'

if __name__ == "__main__":
    take_a_snap()
