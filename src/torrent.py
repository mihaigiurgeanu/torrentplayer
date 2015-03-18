import libtorrent as lt
from time import sleep
import sys
from traceback import print_exception

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

    def pieces(self, h):
        print "pieces(...) called - " + h.name()
        ti = h.get_torrent_info()
        print "Got torrent_info"
        num_pieces = int(ti.num_pieces())
        print "Got num_pieces"
        
        print "Waiting for " + str(num_pieces) + " pieces"
        for p in xrange(0, num_pieces):
            print "Waiting for piece " + str(p) + "/" + str(num_pieces) + "\n"
            while not h.have_piece(p):
                print "Waiting to have piece " + str(p)
                sleep(2)
            print "Reading piece " + str(p)
            h.read_piece(p)
            alerts = []
            found = False
            while True:
                print "Acquire all alerts"
                while True:
                    print "Reading alert"
                    a = self.ses.pop_alert()
                    if not a: break
                    alerts.append(a)

                print "Looking for piece %d in read alerts" % (p)
                for a in alerts:        
                    if type(a) == str:
                        print a
                    else:
                        try:
                            print a.message()
                            print "Checking a.piece()"
                            if a.piece == p:
                                print "Sending piece ", a.piece
                                yield a.buffer
                                found = True
                                break;
                        except:
                            (t, v, tb) = sys.exc_info()
                            print_exception(t, v, tb)
                            
                        else:
                            print "Piece not a match. Searching next"
                print "Exhausted alerts"
                if found: break
                sleep(1)
