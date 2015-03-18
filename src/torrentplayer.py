__author__ = 'Mihai Giurgeanu'

from bottle import post, get, run
from bottle import static_file, redirect
from bottle import request, response
from uuid import uuid4
from torrent import Torrent


torrent = Torrent()
stream_ids = dict()
stream_handles = dict()

@post('/resources/streams')
def create_stream():
    url = request.body.getvalue()
    print "stream request received: " + url
    if url in stream_ids:
        print "The requested downlod already exists: " + stream_ids[url] + "\n"
        
        response.code = 409
        return {
            'url': '/resources/streams/' + stream_ids[url]  + "\n"
        }
    else:
        newid = str(uuid4())
        print "Created new id " + newid + "\n"
        stream_ids[url] = newid
        h = torrent.create_handle(url)
        stream_handles[newid] = h
        
        print "Created new torrent handle for file: " + h.name() + "\n"
        response.status = 201
        newurl = '/resources/streams/' + newid
        response.set_header('Location', newurl)
        return {
            'url': newurl
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
