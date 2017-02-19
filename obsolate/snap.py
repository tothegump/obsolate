# -*- coding:utf8 -*-
import re

REQUEST_MAPPING = {
    'GET': [],
    'POST': [],
    'PUT': [],
    'DELETE': [],
}

HTTP_MAPPINGS = {
    200: '200 OK',
    201: '201 CREATED',
    202: '202 ACCEPTED',
    404: '404 NOT FOUND',
    500: 'INTERNAL SERVER ERROR',
}


class NotFound(Exception):
    pass


class Request(object):
    GET = {}
    POST = {}
    PUT = {}
    DELETE = {}

    def __init__(self, environ):
        self._environ = environ
        # self.setup_self()
        self.path = add_slash(self._environ.get('PATH_INFO', ''))
        self.method = self._environ.get('REQUEST_METHOD', 'GET')
        self.query = self._environ.get('QUERY_STRING', '')
        self.GET = build_query_dict(self.query)


def build_query_dict(query_string):
    pairs = query_string.split('&')
    query_dict = {}
    pair_re = re.compile('^(?P<key>[^=]*?)=(?P<value>.*)')
    for pair in pairs:
        match = pair_re.search(pair)
        if match is not None:
            match_data = match.groupdict()
            query_dict[match_data['key']] = match_data['value']
    return query_dict


def find_matching_url(request):
    if request.method not in REQUEST_MAPPING:
        raise NotFound('not support method :(')
    for url_set in REQUEST_MAPPING[request.method]:
        match = url_set[0].search(request.path)
        if match is not None:
            return (url_set, match.groupdict())
    raise NotFound('Sorry, you got nothing!')


def not_found(environ, start_response):
    start_response(b'404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']


def handle_request(environ, start_response):
    request = Request(environ)
    try:
        (url_set, url, callback), kwargs = find_matching_url(request)
    except NotFound:
        return not_found(environ, start_response)

    output = callback(request, **kwargs)
    content_type = 'text/html'
    status = 200
    try:
        content_type = callback.content_type
    except AttributeError:
        pass
    try:
        status = callback.status
    except AttributeError:
        pass

    start_response(HTTP_MAPPINGS.get(status), [('Content-Type', content_type)])
    return output


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
def index(request):
    return 'Indexed'


@get('/hello')
def greeting(request):
    return 'hello world'


@post('/hello')
def greeting_post(request, **kwargs):
    return 'hi, postman'


@get('/hello/(?P<name>\w+)')
def personal_greeting(request, name=', world'):
    return 'Hello %s!' % name


@post('/hello/(?P<name>\w+)')
def greeting_post(request, name, **kwargs):
    return 'hi, postman, I am {name}'.format(name=name)


if __name__ == "__main__":
    take_a_snap()
