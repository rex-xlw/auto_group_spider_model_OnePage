# -*- coding: utf-8 -*-
import CONFIG as Config
import urllib2
import re
import gzip
import zlib
import StringIO

from lxml import etree
import lxml
import dateutil.parser as dparser
import datetime
import connection
import sys
import time
import HTMLParser
import unidecode
import linecache
from bs4 import BeautifulSoup

import os
sys.path.append(os.path.abspath('../Scripts'))
import dbConnection

reload(sys)
sys.setdefaultencoding('utf-8') 

#####################
#database setting
conn = dbConnection.conn
Agnes = conn.Agnes
itemFilter = conn.itemFilter
groupslowercase = Agnes.groupslowercase
# groups = Agnes.groups_auto
# groups = Agnes.groups
groups = Agnes.groups_udc
######################

visitList = []
visitedList = []
crawledItem = 0

#preset parameter
grpnamePattern = ""
grpdescPattern = ""
grpaddressPattern = ""
grpemailPattern = ""
tagsPattern = []
picurlPattern = ""
contactNamePattern = ""
community = []
mainUrlList = ""
subUrlList = []
grpnameModifiedList = []
grpdescModifiedList = []
grpaddressModifiedList = []
specificAddress = ""
urlPrefixList = []
additionalTags = []
domain = ""
grpsource = ""
grptype = ""
filterElementList = []
grpurlPattern = ""
customHeaders = ""

unqualifiedStarttimeCount = 0
unqualifiedEndtimeCount = 0
unqualifiedFlag = 3

def main():
	load_element()
	visit()

def visit():
	global mainUrlList

	visitList.extend(mainUrlList)
	visit_page()

def load_element():
	global grpnamePattern
	global grpdescPattern
	global grpaddressPattern
	global grpemailPattern
	global tagsPattern
	global picurlPattern
	global community
	global mainUrlList
	global subUrlList
	global grpnameModifiedList
	global grpdescModifiedList
	global grpaddressModifiedList
	global specificAddress
	global urlPrefixList
	global additionalTags
	global domain
	global grpsource
	global grptype
	global filterElementList
	global contactNamePattern
	global grpurlPattern
	global customHeaders
	global recordXPath

	grpnamePattern = Config.grpname
	grpdescPattern = Config.grpdesc
	grpaddressPattern = Config.grpaddress
	grpemailPattern = Config.grpemail
	community = Config.community
	grpsource = Config.source
	mainUrlList = Config.mainUrlList
	subUrlList = Config.subUrlList
	domain = Config.domain
	grptype = Config.grptype
	urlPrefixList = Config.urlPrefixList
	filterElementList = Config.filterElementList
	picurlPattern = Config.picurl
	additionalTags = Config.additionalTags
	tagsPattern = Config.tags
	grpnameModifiedList = Config.grpnameModifiedList
	grpdescModifiedList = Config.grpdescModifiedList
	grpaddressModifiedList = Config.grpaddressModifiedList
	specificAddress = Config.specificAddress
	contactNamePattern = Config.contactName
	grpurlPattern = Config.grpurl
	customHeaders = Config.customHeaders
	recordXPath = Config.recordXPath

	if grpsource == "":
		grpsource = re.sub(r'https?:(//)?(www\.)?', '', mainUrlList[0])
		grpsource = re.sub(r'(?<=com|net|edu|org)/[\w\W]*', '', grpsource)

	if domain == "":
		domain = re.sub(r'(?<=com|net|edu|org)/[\w\W]*', '', mainUrlList[0])


def visit_page():
	global visitList
	global visitedList
	global crawledItem

	while len(visitList) != 0:
		requrl = visitList[0]
		# try:
		#check custom header
		if customHeaders == "":
			req = urllib2.Request(requrl)
		else:
			req = urllib2.Request(requrl, headers = customHeaders)

		res_data = urllib2.urlopen(req, timeout = 10)
		encoding = res_data.info().get('Content-Encoding')
		
		if encoding in ('gzip','x-zip','deflate'):
			res = decode(res_data, encoding)
		else:
			res = res_data.read()

		analyze_page(res, requrl)

		print requrl

		# except Exception as e:
		# 	print "#######################################"
		# 	print "Exception handling: " + str(e)
		# 	print requrl
		# 	printException()
		# 	print "#######################################"
			
		visitList.remove(requrl)
		visitedList.append(requrl)
		#print visitedList
		#raw_input("visitList")
		
		#sys.stdout.write('visited quantity: '+ str(len(visitedList))+ "\r")
		#sys.stdout.flush()

		#print visitedList
		#print visitList
		#raw_input("123")


	time.sleep(0.5)
	print
	print "visited quantity: " + str(len(visitedList))
	print "crawledItem: " + str(crawledItem)
	#print visitList
	#print visitedList

def decode(res_data, encoding):
	res = res_data.read()
	if encoding == "deflate":
		data = StringIO.StringIO(zlib.decompress(res))
	else:
		data = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(res))
	res = data.read()
	return res

def analyze_page(HTML, requrl):
	#remove script content
	HTML = re.sub(r'<script[\w\W]*?</script>', '', HTML)
	HTML = re.sub(r'<!--[\w\W]*?-->', '', HTML)
	HTML = HTMLParser.HTMLParser().unescape(HTML)
	soup = BeautifulSoup(HTML)
	HTML = str(soup.body)
	#print HTML
	#raw_input("HTML")
	divideGroup(HTML, requrl)


def divideGroup(HTML, requrl):
	global recordXPath
	parser = etree.XMLParser(recover = True)
	tree = etree.fromstring(HTML, parser)

	groupLxmlItems = tree.xpath(recordXPath)
	for groupLxmlItem in groupLxmlItems:
		fetch_information(groupLxmlItem, requrl)

def modifyUrl(url):
	global subUrlList
	url = HTMLParser.HTMLParser().unescape(url)
	for subUrl in subUrlList:
		url = re.sub(subUrl, "", url)
	return url

def checkUselessUrl(url):
	global filterElementList
	isUseless = False
	uselessList = filterElementList
	for useless in uselessList:
		if useless in url.lower():
			isUseless = True
			break
	return isUseless

def fetch_information(groupLxmlItem, requrl):
	global grpnamePattern
	global grpdescPattern
	global grpaddressPattern
	global grpemailPattern
	global community
	global grpsource
	global grptype
	global picurlPattern
	global tagsPattern
	global additionalTags
	global specificAddress
	global contactNamePattern
	global grpurlPattern
	global recordXPath

	currentTime =  datetime.datetime.now()
	currentDate = currentTime.strftime('%Y-%m-%d')
	currentDate = datetime.datetime.strptime(currentDate, '%Y-%m-%d')
	formerDate = currentDate + datetime.timedelta(days=-1)
	
	grpname = ""
	grpdesc = ""
	grpaddress = ""
	picurl = ""
	tags = []
	grpurl = ""
	contactName = ""
	#raw_input(requrl)
	#print HTML
	#raw_input(123)

	grpname = groupLxmlItem.find(grpnamePattern)
	if grpname == None:
		print "row data are not qualified"
		return 0
	grpname = get_text(grpname)

	if grpdescPattern != "":
		grpdesc = groupLxmlItem.find(grpdescPattern)
		grpdesc = get_text(grpdesc)

	if grpemailPattern != "":
		grpemail = groupLxmlItem.find(grpemailPattern)
		grpemail = get_emailText(grpemail)
	else:
		grpemail = ""

	if contactNamePattern != "":
		contactName = groupLxmlItem.find(contactNamePattern)
		contactName = get_text(contactName)

	if specificAddress != "":
		grpaddress = specificAddress

	if grpname == "":
		print "grpname unqualified: ",
		print requrl
		return 0

	if grpaddressPattern != "":
		grpaddress = groupLxmlItem.find(grpaddressPattern)
		grpaddress = get_text(grpaddress)

	if picurlPattern != "":
		picurl = groupLxmlItem.find(picurlPattern)
		picurl = get_picurl(picurl)


	if tagsPattern != "":
		tags = groupLxmlItem.find(tagsPattern)
		tags = get_text(tags)
		tags = analyze_tags(tags)

	if grpurlPattern != "":
		grpurl = groupLxmlItem.find(grpurlPattern)
		grpurl = get_groupUrl(grpurl)

	if "www" not in picurl and "http" not in picurl and "https" not in picurl and picurl != "":
		picurl = domain + "/" + picurl
	#raw_input(picurl)

	url = requrl

	if " " in grpemail:
		grpemail = grpemail.split(" ")
	elif "/" in grpemail:
		grpemail = grpemail.split("/")
	elif grpemail == "":
		grpemail = []
	else:
		grpemail = [grpemail]

	temp = []
	for email in grpemail:
		temp.append(email.strip())
	grpemail = temp

	fetch_data(url, grpname, grpdesc, grpaddress, community, grpsource, formerDate, tags, additionalTags, picurl, contactName, grpemail, grptype, grpurl)

def get_picurl(lxmlItems):
	picurl = ""
	for lxmlItem in lxmlItems:
		picurlText = lxmlItem.get("style")
		if picurlText != None:
			picurl += picurlText
	if "background-image" in picurl:
		picurl = re.sub(r"^[\w\W]*background-image:\s*url\(\'", "", picurl)
		picurl = re.sub(r"\'\)[\w\W]*$", "", picurl)
	else:
		picurl = ""
		for lxmlItem in lxmlItems:
			picurl += lxmlItem.get("src")
			picurl = re.sub(r"^\W*?(?=\w)", "", picurl)
	return picurl

def get_text(lxmlItems):
	text = ""
	text = etree.tostring(lxmlItems)
	text = re.sub(r'<[\w\W]*?>', '', text)
	text = text.strip()
	text = re.sub(r'\n', '/', text)

	return text
	# text = ""
	# for lxmlItem in lxmlItems:
	# 	if isinstance(lxmlItem, unicode) or isinstance(lxmlItem, str):
	# 		text = text + "\n" + lxmlItem
	# 	else:
	# 		for item in lxmlItem.itertext():
	# 			text = text + "\r\n" + item
	# text = text.strip()
	# return text

def get_emailText(lxmlItems):
	text = ""
	text = etree.tostring(lxmlItems)
	if "mailto:" in text:
		text = re.sub(r'[\w\W]*mailto:', '', text)
		text = re.sub(r'[\"|\'][\w\W]*', '', text)
	else:
		text = re.sub(r'<[\w\W]*?>', '', text)
		text = text.strip()
		text = re.sub(r'\n', '/', text)
	return text

def get_groupUrl(lxmlItems):
	text = ""
	text = etree.tostring(lxmlItems)

	if "href" in text:
		text = re.sub(r'[\w\W]*href=[\"|\']', '', text)
		text = re.sub(r'[\"|\'][\w\W]*', '', text)
	else:
		text = re.sub(r'<[\w\W]*?>', '', text)
		text = text.strip()
		text = re.sub(r'\n', '/', text)

	return text

def analyze_tags(tags):
	tagsSplitCharList = [",", "|", ";", "\\", "/", "."]
	tagsSplitChar = ""
	for tagsSplitCharItem in tagsSplitCharList:
		if tagsSplitCharItem in tags:
			tagsSplitChar = tagsSplitCharItem
			break
	if tagsSplitChar != "":
		tagsList = tags.split(tagsSplitChar)
	else:
		tagsList = [tags]		
	return tagsList

def modify_grpname(grpname):
	global grpnameModifiedList

	for grpnameModifiedItem in grpnameModifiedList:
		grpname = re.sub(grpnameModifiedItem, '', grpname)
	return grpname

def modify_grpdesc(grpdesc):
	global grpdescModifiedList

	for grpdescModifiedItem in grpdescModifiedList:
		grpdesc = re.sub(grpdescModifiedItem, '', grpdesc)
	return grpdesc

def modify_grpaddress(grpaddress):
	global grpaddressModifiedList

	for grpaddressModifiedItem in grpaddressModifiedList:
		grpaddress = re.sub(grpaddressModifiedItem, '', grpaddress)
	return grpaddress

def lowerKeywords(keywords):
	returnKeywords = []
	for keyword in keywords:
		returnKeywords.append(keyword.lower())
	return returnKeywords

def decide_group_gender(grpname, grpdesc, keywords):
	womenGrpnameKeywordList = ["all-female", "all female", "panhellenic", "women's club", "womens club", "club softball"]
	womenKeywordsList = ["all-female", "all female"]
	womenGrpdescKeywordList = ["all-female", "all female"]
	menGrpnameKeywordList = ["interfraternity", "men's club", "mens club", "club baseball"]
	menKeywordsList = ["all-male", "all male"]
	menGrpdescList = ["all-male", "all male"]

	keywords = lowerKeywords(keywords)
	grpname = grpname.lower()
	grpdesc = grpdesc.lower()

	for womenGrpnameKeyword in womenGrpnameKeywordList:
		if womenGrpnameKeyword in grpname:
			return "female"
	for womenKeyword in womenKeywordsList:
		if womenKeyword in keywords:
			return "female"
	for womenGrpdescKeyword in womenGrpdescKeywordList:
		if womenGrpdescKeyword in grpdesc:
			return "female"
	for menGrpnameKeyword in menGrpnameKeywordList:
		if menGrpnameKeyword in grpname:
			return "male"
	for menKeyword in menKeywordsList:
		if menKeyword in keywords:
			return "male"
	for menGrpdesc in menGrpdescList:
		if menGrpdesc in grpdesc:
			return "male"
	return "both"

def decide_group_audience(keywords, grpname):
	graduateKeywordList = ["grad", "grad student", "grad students", "graduate student", "graduate students"]
	graduateGrpnameList = [" graduate", " graduates", " grads"]
	
	keywords = lowerKeywords(keywords)
	grpname = grpname.lower()

	for graduateKeyword in graduateKeywordList: 
		if graduateKeyword in keywords:
			return "grad"
	for graduateGrpname in graduateGrpnameList:
		if graduateGrpname in grpname:
			return "grad"
	return "both"
	
def fetch_data(url, grpname, grpdesc, grpaddress, community, grpsource, formerDate, tags, additionalTags, picurl, contactName, grpemail, grptype, grpurl):

	grpname = modify_grpname(grpname)
	grpdesc = modify_grpdesc(grpdesc)
	grpaddress = modify_grpaddress(grpaddress)
	grpGender = decide_group_gender(grpname, grpdesc, tags)
	audience = decide_group_audience(tags, grpname)
	if "/" in grpemail:
		grpemailList = grpemail.split("/")
	if grptype == "":
		grptype = "private"
	feed_item(url, grpname, grpdesc, grpaddress, community, grpsource, formerDate, tags, additionalTags, picurl, contactName, grpemail, grpGender, audience, grptype, grpurl)

def feed_item(url, grpname, grpdesc, grpaddress, community, grpsource, formerDate, tags, additionalTags, picurl, contactName, grpemail, grpGender, audience, grptype, grpurl):
	item = {}
	item["grpname"] = HTMLParser.HTMLParser().unescape(grpname).encode("ascii","ignore").encode("ascii","ignore")
	item["grpaddress"] = HTMLParser.HTMLParser().unescape(grpaddress).encode("ascii","ignore")
	item["grpdesc"] = HTMLParser.HTMLParser().unescape(grpdesc).encode("ascii","ignore")
	item["grpemail"] = grpemail
	item["createdate"] = formerDate
	item["community"] = community
	item["picurl"] = picurl
	item["keywords"] = []
	
	item["weburl"] = []
	item["weburl"].append(url)
	if grpurl != "":
		item["weburl"].append(grpurl)
	
	item["grptype"] = grptype
	item["status"] = True

	item["audience"] = audience
	item["members"] = []
	item["memcount"] = len(item["members"])
	item["pendingreq"] = []

	item["events"] = []
	item["evtcount"] = len(item["events"])
	item["admin"] = []
	item["gender"] = grpGender
	
	item["grpsource"] = grpsource
	item["other"] = {"tags":tags}
	if contactName != "":
		item["other"]["contact name"] = contactName
	item["other"]["tags"].extend(additionalTags)
	item["just_crawled"] = True
	item["isAvailable"] = True

	print item
	raw_input("item")

	#insert_item(item)

def insert_item(item):
	global crawledItem

	print "Insert!"
	crawledItem += 1
	print item["grpname"]
	#print item
	# raw_input(item["weburl"][0])
	
	inserted_id = groups.insert(item)
	insertGroupForKazem(item, inserted_id)

def insertGroupForKazem(group, inserted_id):
	try:
		group["groups_id"] = inserted_id
		group["grpname"] = group["grpname"].lower()
		group["grpaddress"] = group["grpaddress"].lower()
		group["grpdesc"] = group["grpdesc"].lower()
		tagList = []
		for tag in group["other"]["tags"]:
			tagList.append(tag.lower())
		group["other"]["tags"] = tagList
		groupslowercase.insert(group)
	except Exception as e:
		print "#########################"
		print "ERROR:"
		print e
		print "#########################"
		groupslowercase.insert(group)

def printException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

if __name__ == '__main__':
	main()


	