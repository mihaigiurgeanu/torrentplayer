from gevent import monkey; monkey.patch_all()

from bottle import post, get, run
from bottle import static_file, redirect
from bottle import request, response
from uuid import uuid4
from torrent import Torrent
import mimetypes; mimetypes.init()

import gevent.queue


torrent = Torrent()
stream_ids = dict()
stream_handles = dict()

@post('/resources/streams')
def create_stream():
    url = request.body.getvalue()
    print "stream request received: " + url
    if url in stream_ids:
        print "The requested downlod already exists: " + stream_ids[url] + "\n"
        
        response.status = 409
        return {
            'url': '/resources/streams/' + stream_ids[url]  + "\n"
        }
    else:
        h = torrent.create_handle(url)
        newid = h.get_torrent_info().name()
        print "Created new id " + newid + "\n"
        stream_ids[url] = newid

        stream_handles[newid] = h
        
        print "Created new torrent handle for file: " + h.get_torrent_info().name() + "\n"
        response.status = 201
        newurl = '/resources/streams/' + newid
        response.set_header('Location', newurl)
        return {
            'url': newurl
        }

@get('/resources/streams/<stream>')
def get_stream(stream):
    if stream in stream_handles:
        print "Playing media " + stream
        h = stream_handles[stream]
        (content_type, encoding) = mimetypes.guess_type(h.get_torrent_info().name())

        if content_type:
            print "Media type is " + content_type
        else:
            print "Media type could not be guessed"
            
        if content_type:
            response.set_header("Content-Type", content_type)
            
        body = gevent.queue.Queue()
        torrent.register(h, body)
        return body
    else:
        print "Stream does not exist " + stream
        response.code = 404
        return "Stream does not exists for id " + stream
    
    

@get('/')
def get_home():
    redirect('/index.html')

@get('/<filepath:path>')
def get_static(filepath):
    return static_file(filepath, root='./resources/public')

run(host='0.0.0.0', port=8080, debug=True, server='gevent')
