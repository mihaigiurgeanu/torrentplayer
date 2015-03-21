import libtorrent as lt
import sys
from traceback import print_exception
from threading import Lock, Thread, Event
import gevent

class Torrent:
    def __init__(self):
        print "Creating a new torrent session\n"
        settings = lt.session_settings()
        settings.user_agent = 'torrentplayer v0.1.1/' + lt.version
        
        self.ses = lt.session()
        self.ses.set_download_rate_limit(int(0))
        self.ses.set_upload_rate_limit(int(0))
        self.ses.listen_on(6781, 6991)
        self.ses.set_settings(settings)
        self.ses.set_severity_level(lt.alert.severity_levels.debug)
        self.ses.add_extension(lt.create_ut_pex_plugin)
        self.ses.add_extension(lt.create_ut_metadata_plugin)
        self.ses.add_extension(lt.create_metadata_plugin)
        self.ses.add_extension(lt.create_smart_ban_plugin)
        # self.ses.set_alert_mask(lt.alert.category_t.progress_notification 
        #     | lt.alert.category_t.error_notification 
        #     | lt.alert.category_t.peer_notification
        #     | lt.alert.category_t.storage_notification
        #     | lt.alert.category_t.tracker_notification
        #     | lt.alert.category_t.status_notification
        #     | lt.alert.category_t.debug_notification)
        #self.ses.set_alert_mask(lt.alert.category_t.all_categories)

        try:
            self.ses.start_dht()
        except:
            (t, v, tb) = sys.exc_info()
            print_exception(t, v, tb)
            print "DHT is not running"

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
        h = lt.add_magnet_uri(self.ses, magnet, {'save_path': '/home/ubuntu/workspace/resources/downloads'})
        h.set_max_connections(60)
        h.set_max_uploads(-1)
        h.set_ratio(0)
        h.set_sequential_download(True)
        while not h.has_metadata():
		    gevent.sleep(5)
		
        return h

    def dispatch_alerts(self):
        while not self.stop_event.is_set():
            alert = self.ses.pop_alert()
            if not alert: break
            if type(alert) == str:
                print alert
            else:
                #print alert.message()
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
                        print "Check if piece %d is available for %s" % (p, h.name())
                        if h.have_piece(p):
                            print "%s: Piece %d is available. Ask for reading it" % (h.name(), p)
                            self.requests[i] = (h, p, q, True)
                            h.read_piece(p)
            finally:
                self.requests_lock.release()
