#def readURL(callback):
	
#def setURL(addrs):
import urllib.request
class SpiderX:
	def __init__(self,urls):
		'''
		urls: list of urls want to be looked
		'''
		self._urls = urls
		self._content = []

	def crawl(self, callback = None):
		html =  urllib.request.urlopen(self._urls[0]).read()
		print(html)
		
	
	

if __name__ == "__main__":
	s = SpiderX(['http://google.ca/'])
	s.crawl()

