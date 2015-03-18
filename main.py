from torrent import Torrent
import time


def main():
	
	MAGNET = 'magnet:?xt=urn:btih:92330CE485E11D6B3F083240121B148A0325C4AF&dn=vice+2015+french+brrip+xvid+ac3+destroy+avi&tr=http%3A%2F%2Fannounce.torrentsmd.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'
	#The path must exist, else download stay at 0%.
	FILE_OUT_PATH = './resources/downloads'
	PORT_RANGE_START = 6781
	PORT_RANGE_END = 6991
	
	t1 = Torrent(PORT_RANGE_START,PORT_RANGE_END)
	t1.startDowloadFromMagnet(MAGNET,FILE_OUT_PATH)
	
	
	i = 0	
	while not t1.isComplete():
		
		if not t1.isComplete():
			print 'Dowload info: ' + t1.getFileName()
			print 'Dowload: ' + str(t1.getDowloadRate()) + ' Kbps \n'\
				  'Upload: ' + str(t1.getUploadRate()) + ' Kbps \n' \
				  'Progress: ' + str(t1.getProgress()) + ' % \n' \
				  'Status: '  + t1.getDowloadStatus() + '\n' \
				  'Peers: ' + str(t1.getNumPeers()) + '\n' \
				  'Remaining time: ' + str(t1.getRemainingTime()) + ' seconds\n'\
				  'Size : ' + str(t1.getTotalSize()) + ' Bytes' '\n\n'
			
		time.sleep(3)
		
	return 0


if __name__ == '__main__':
	main()
