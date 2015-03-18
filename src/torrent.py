import libtorrent as lt
from time import sleep
import sys
from traceback import print_exception
from threading import Lock, Thread

class Torrent:
    def __init__(self):
        print "Creating a new torrent session\n"
        self.ses = lt.session()
        self.ses.listen_on(6781, 6991)
        self.requests = []
        self.requests_lock = Lock()
        self.alerts_thread = Thread(target = (lambda: self.process_alerts_loop()))
        self.wait_for_pieces_thread = Thread(target = (lambda: self.wait_for_pieces()))
        self.alerts_thread.start()
        self.wait_for_pieces_thread.start()

    def register(self, h, q):
        self.requests_lock.acquire()
        try:
            print "Registering new request: ", h.name()
            self.requests.append((h, 0, q))
        finally:
            self.requests_lock.release()
        

    def create_handle(self, magnet):	
		h = lt.add_magnet_uri(self.ses, magnet, {'save_path': './resources/downloads'})
		h.set_sequential_download(True)
		while not h.has_metadata():
		    sleep(5)
		
		return h

    def process_alerts_loop(self):
        while True:
            try:
                alert = self.ses.pop_alert()
                if not alert:
                    sleep(0.5)
                    continue
                if type(alert) == str:
                    print alert
                else:
                    print alert.message()
                    if hasattr(alert, 'piece') and hasattr(alert, 'buffer') and hasattr(alert, 'handle'):
                        self.process_read_piece_alert(alert)
                    
            except:
                (t, v, tb) = sys.exc_info()
                print_exception(t, v, tb)

    def process_read_piece_alert(self, a):
        self.requests_lock.acquire()
        try:
            for i in range(0, len(self.requests)):
                (h, p, q) = self.requests[i]
                if h.name() == a.handle.name() and p == a.piece:
                    print "Sending piece %d to the client of %s" % (p, h.name()) 
                    q.put(a.buffer)
                    nextp = p + 1
                    if nextp >= h.get_torrent_info().num_pieces():
                        del self.requests[i]
                        q.put(StopIteration)
                    else:
                        self.requests[i] = (h, nextp, q)
                    break
        finally:
            self.requests_lock.release()
    
    def wait_for_pieces(self):
        while True:
            self.requests_lock.acquire()
            try:
                for (h, p, q) in self.requests:
                    print "Check if piece %d is available for %s" % (p, h.name())
                    if h.have_piece(p):
                        print "Piece is available"
                        h.read_piece(p)
            finally:
                self.requests_lock.release()
            sleep(0.5)