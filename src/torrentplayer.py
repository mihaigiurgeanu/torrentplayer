__author__ = 'Mihai Giurgeanu'

from bottle import post, get, run
from bottle import static_file, redirect
from bottle import request, response

@post('/resources/streams')
def create_stream():
    print "stream request received: " + request.body.forms.url
    response.status = 201
    response.set_header('Location', '/resources/streams/12345')
    return {
        'url': '/resources/streams/12345',
        'type': 'mp4'
    }

@get('/resources/streams/<stream>')
def get_stream(strem):
    return "Hello World 2!"

@get('/')
def get_home():
    redirect('/index.html')

@get('/<filepath:path>')
def get_static(filepath):
    return static_file(filepath, root='./resources/public')

run(host='0.0.0.0', port=3000, debug=True)
