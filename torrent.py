import libtorrent as lt
import sys
from traceback import print_exception
from threading import Lock, Thread, Event
import gevent

class Torrent:
    def __init__(self):
        print "Creating a new torrent session\n"
        self.ses = lt.session()
        self.ses.listen_on(6781, 6991)
        self.ses.set_alert_mask(lt.alert.category_t.progress_notification)
        self.requests = []
        self.requests_lock = Lock()
        self.alerts_thread = Thread(target = (lambda: self.process_alerts_loop()))
        self.stop_event = Event()


    def start(self):
        self.alerts_thread.start()

    def stop(self):
        self.stop_event.set()
        self.alerts_thread.join(10)
        if self.alerts_thread.is_alive():
            print "The alerts thread did not stop"
        
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
		    gevent.sleep(5)
		
		return h

    def dispatch_alerts(self):
        while not self.stop_event.is_set():
            alert = self.ses.pop_alert()
            if type(alert) == str:
                print alert
            else:
                if type(alert) == lt.read_piece_alert:
                    self.process_read_piece_alert(alert)
                    self.check_required_pieces()
                if type(alert) == lt.piece_finished_alert:
                    self.check_required_pieces()
                    
    def process_alerts_loop(self):
        while not self.stop_event.is_set():
            try:
                alert = self.ses.wait_for_alert(2000)
                if alert:
                    self.dispatch_alerts()
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
