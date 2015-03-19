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
        self.ses.set_alert_mask(lt.alert.category_t.progress_notification)
        self.requests = []
        self.requests_lock = Lock()
        self.alerts_thread = Thread(target = (lambda: self.process_alerts_loop()))
        self.alerts_thread.start()
       
    def register(self, h, q):
        self.requests_lock.acquire()
        try:
            print "Registering new request: ", h.name()
            self.requests.append((h, 0, q, False))
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
                    sleep(0.02)
                    continue
                if type(alert) == str:
                    print alert
                else:
                    #print type(alert).__name__, ": ", alert.message()
                    #if hasattr(alert, 'piece') and hasattr(alert, 'buffer') and hasattr(alert, 'handle'):
                    if type(alert) == lt.read_piece_alert:
                        self.process_read_piece_alert(alert)
                        self.check_required_pieces()
                    if type(alert) == lt.piece_finished_alert:
                        self.check_required_pieces()
                    
            except:
                (t, v, tb) = sys.exc_info()
                print_exception(t, v, tb)

    def process_read_piece_alert(self, a):
        self.requests_lock.acquire()
        try:
            for i in range(0, len(self.requests)):
                (h, p, q, f) = self.requests[i]
                if h.name() == a.handle.name() and p == a.piece:
                    print "Sending piece %d to the client of %s" % (p, h.name()) 
                    q.put(a.buffer)
                    nextp = p + 1
                    if nextp >= h.get_torrent_info().num_pieces():
                        del self.requests[i]
                        q.put(StopIteration)
                    else:
                        self.requests[i] = (h, nextp, q, False)
                    break
        finally:
            self.requests_lock.release()
    
    def check_required_pieces(self):
            self.requests_lock.acquire()
            try:
                for i in range(0, len(self.requests)):
                    (h, p, q, f) = self.requests[i]
                    if not f:
                        #print "Check if piece %d is available for %s" % (p, h.name())
                        if h.have_piece(p):
                            #print "Piece is available"
                            self.requests[i] = (h, p, q, True)
                            h.read_piece(p)
            finally:
                self.requests_lock.release()
