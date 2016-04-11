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

	def crawl(self, callback):
		'''
		callback: user define callback to parse html content for each url.
		callback: returns will be push into _content 
		'''
		for url in self._urls:
			self._content.append(callback
								(urllib.request.urlopen
									(url).read()))
	def watch(self):
		return self._content		
	
	

if __name__ == "__main__":
	def plain(html):
		return html
	s = SpiderX(['http://google.ca/'])
	s.crawl(plain)
	print(s.watch())

