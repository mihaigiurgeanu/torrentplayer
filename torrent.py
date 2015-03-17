import libtorrent as lt


class Torrent:


	def __init__(self, frm, to):
	
		self.ses = lt.session()
		self.ses.listen_on(frm, to)
			
	
	def startDowloadFromMagnet(self,magnet,outPath):	
	
		self.h = lt.add_magnet_uri(self.ses,magnet, {'save_path': outPath})
		self.h.set_sequential_download(True)		
		
	
	def getTotalSize(self):
	
		s = self.h.status()
		return s.total_wanted


	def getRemainingTime(self):
	
		s = self.h.status()
		dr = s.upload_rate
		
		if dr == 0:
			return -1
		return self.getTotalSize() / (dr*8)
	
	def getFileName(self):
	
		return self.h.name()	
		
	def getNumPeers(self):
	
		if self.isComplete():
			return 0
		else:
			s = self.h.status()
			return s.num_peers
	
	def getUploadRate(self):		
	
		if self.isComplete():
			return 0
		else:
			s = self.h.status()
			return s.upload_rate/1000	
		
	
	def getDowloadRate(self):		
		
		if self.isComplete():
			return 0
		else:
			s = self.h.status()
			return s.download_rate/1000
	
	def getProgress(self): 
		
		if self.isComplete():
			return 0
		else:
			s = self.h.status()
			return s.progress * 100
	
	def getDowloadStatus(self):
	
		s = self.h.status()
		
		state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
		
		if self.isComplete():
			
			return 'complete'			
		
		else:	
		
			return state_str[s.state]
	
	def isComplete(self):
		
		s = self.h.status()
		
		return self.h.is_seed()
		
