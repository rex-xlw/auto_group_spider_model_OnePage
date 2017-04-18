#input xpath
grpname = './/strong/a'
grpdesc = '.'
grpaddress = ''
grpemail = ''
tags = ''
contactName = ''
grpurl = './/a'

#all the picurl should be included in the src tag
picurl = ''
#input the list of community
community = ["gmu", "groupten"]

#xpath for each single group
recordXPath = '//div[@class="entry-content"]/ul/li'

#input url #format: "http(s)://xx.xxx.edu(com/net)/xxx/xxx/xxx" The domain name should be the same
mainUrlList = [
				'http://ulife.gmu.edu/about-us/offices-of-university-life/',
				]
				

#remove url partial pattern
subUrlList = []

#element modify list
grpnameModifiedList = []
grpdescModifiedList = []
grpaddressModifiedList = []

#input specific location, can ignore
specificAddress = ''

#input a list of half regualr experssion
urlPrefixList = []

#input addtional tags for the crawlers
additionalTags = []

#input domain, can ignore
domain = ''

#input grpsource, can ignore
source = ''

#input grptype, can ignore
grptype = ''

#Preset parameter
filterElementList = ['.jpg', '.css', '.png', '.js', '.ico', '.pdf', '.docx', '.jpeg']

#custom header
customHeaders = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
			'Accept-Encoding': 'none',
			'Accept-Language': 'en-US,en;q=0.8',
			'Connection': 'keep-alive',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
			}