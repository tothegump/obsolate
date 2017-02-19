# -*- coding:utf8 -*-
import re

REQUEST_MAPPING = {
    'GET': [],
    'POST': [],
    'PUT': [],
    'DELETE': [],
}


class NotFound(Exception):
    pass


def find_matching_url(environ, start_response):
    request_method = environ.get('REQUEST_METHOD', 'GET')
    if request_method not in REQUEST_MAPPING:
        raise NotFound('not support method :(')
    path = add_slash(environ.get('PATH_INFO', ''))
    for url_set in REQUEST_MAPPING[request_method]:
        match = url_set[0].search(path)
        if match is not None:
            return (url_set, match.groupdict())
    raise NotFound('Sorry, you got nothing!')


def not_found(environ, start_response):
    start_response(b'404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']


def handle_request(environ, start_response):
    try:
        (url_set, url, callback), kwargs = find_matching_url(environ, start_response)
        print (url_set, url, callback)
    except NotFound:
        return not_found(environ, start_response)
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return callback(**kwargs)


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
def add_slash(url):
    if not url.endswith('/'):
        url = '{}/'.format(url)
    return url


def get(url):
    def wrapped(func):
        def new(*args, **kwargs):
            return func(*args, **kwargs)
        # Register.
        re_url = re.compile('^{path}$'.format(path=add_slash(url)))
        REQUEST_MAPPING['GET'].append((re_url, url, new))
        return new
    return wrapped


def post(url):
    def wrapped(func):
        def new(*args, **kwargs):
            return func(*args, **kwargs)
        re_url = re.compile('^{path}$'.format(path=add_slash(url)))
        REQUEST_MAPPING['POST'].append((re_url, url, new))
        return new
    return wrapped


@get('/')
def index():
    return 'Indexed'


@get('/hello')
def greeting():
    return 'hello world'


@post('/hello')
def greeting_post(**kwargs):
    print kwargs
    return 'hi, postman'


@get('/hello/(?P<name>\w+)')
def personal_greeting(name=', world'):
    return 'Hello %s!' % name


@post('/hello/(?P<name>\w+)')
def greeting_post(name, **kwargs):
    print kwargs
    return 'hi, postman, I am {name}'.format(name=name)


if __name__ == "__main__":
    take_a_snap()
