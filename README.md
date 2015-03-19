# README #

The torrentplayer is a RESTful server that accepts a torrent magnet URI in a POST request and
returns the content of the downloaded file sequentially in a way suitable for playing in a web page.

### What is this repository for? ###

* An HTTP streaming server for content downloaded from bittorrent.
* 0.1.0-SNAPSHOT

### How do I get set up? ###

After downloading the file you just need to unzip the archive on
a directory on your local computer.

In command line, you will issue:

    #> python torrentplayer.py

#### Dependencies

* python 2.7
* bottle framework

    $ pip install bottle
    
* libtorrent
    
    $ apt-get install libtorrent

* gevent
    
    $ pip install gevent

For windows there are windows installers for gevent.

#### Customizing configuration

You can edit main file, torrentplayer.py to customize the default settings:

    * edit the port and the host to listen in the last line of torrentpalyer.py

### Issues

* There is no control over the downloading process. One cannot manage the downloading
    proccess, it can be just started.
* If you stop watching the movie the download process dose not stop.
* There can be a REST api call that shows the current media, so the user could click
    directly on a link and watch a movie that has already started to download.
