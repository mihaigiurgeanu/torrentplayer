import libtorrent as lt
from time import sleep

class Torrent:
    def __init__(self):
        print "Creating a new torrent session\n"
        self.ses = lt.session()
        self.ses.listen_on(6781, 6991)

    def create_handle(self, magnet):	
		h = lt.add_magnet_uri(self.ses, magnet, {'save_path': './resources/downloads'})
		h.set_sequential_download(True)
		while not h.has_metadata():
		    sleep(5)
		
		return h
