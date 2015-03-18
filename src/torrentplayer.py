__author__ = 'Mihai Giurgeanu'

from bottle import post, get, run
from bottle import static_file, redirect
from bottle import request, response

@post('/resources/streams')
def create_stream():
    print "stream request received: " + request.body.getvalue()
    response.status = 201
    response.set_header('Location', '/resources/streams/12345')
    return {
        'url': '/resources/streams/small.ogv',
        'type': 'mp4'
    }

@get('/resources/streams/<stream>')
def get_stream(stream):
    print "Playing video " + stream
    return static_file(stream, root="./resources/downloads");

@get('/')
def get_home():
    redirect('/index.html')

@get('/<filepath:path>')
def get_static(filepath):
    return static_file(filepath, root='./resources/public')

run(host='0.0.0.0', port=8080, debug=True)
