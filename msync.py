#!/usr/bin/env python
# -*- coding: utf-8 -*-

#to ensure the utf8 encoding environment
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
import base64
import re
import htmlentitydefs
import traceback
import random
import ConfigParser
import urllib,urllib2,Cookie
from google.appengine.api import urlfetch
from google.appengine.ext import db

class Twitter(db.Model):
    id=db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

def make_cookie_header(cookie):
    ret = ""
    for val in cookie.values():
        ret+="%s=%s; "%(val.key, val.value)
    return ret

def unescape(text):
   """Removes HTML or XML character references 
      and entities from a text string.
   from Fredrik Lundh
   http://effbot.org/zone/re-sub.htm#unescape-html
   """
   def fixup(m):
       text = m.group(0)
       if text[:2] == "&#":
           # character reference
           try:
               if text[:3] == "&#x":
                   return unichr(int(text[3:-1], 16))
               else:
                   return unichr(int(text[2:-1]))
           except ValueError:
               pass
       else:
           # named entity
           try:
               text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
           except KeyError:
               pass
       return text # leave as is
   return re.sub("&#?\w+;", fixup, text)

def getLatest():
    msg=db.GqlQuery("SELECT * FROM Twitter ORDER BY created DESC")
    x=msg.count()
    if x:
        return msg[0].id
    else:
        return ""

def deleteData(since_id):
    if since_id:
        q = db.GqlQuery("SELECT * FROM Twitter Where id < :1", since_id) 
        results = q.fetch(100) 
        db.delete(results)
        return True
    else:
        return False

def send_plurk_msgs(username,password,msg):
    try:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        api_key = 'mEbS6C00iP1vYlfiy6n1OcfWpwpYwbQX'
        get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
        encode = urllib.urlencode
        fp = opener.open(get_api_url('/Users/login'),
                     encode({'username': username,
                             'password': password,
                             'api_key': api_key}))
        fp.read()
        fp = opener.open(get_api_url('/Timeline/plurkAdd'),
                     encode({'content': msg,
                             'qualifier': 'says',
                             'lang': 'en',
                             'api_key': api_key}))
        fp.read()
        print "plurk,"
    except:
        return traceback.print_exc()

def send_sina_msgs(username,password,msg):
    try:
        auth=base64.b64encode(username+":"+password)
        auth='Basic '+auth
        msg=unescape(msg)
        form_fields = {
            "status": msg,
            }
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url="http://api.t.sina.com.cn/statuses/update.xml?source=2768348656",
            payload=form_data,
            method=urlfetch.POST,
            headers={'Authorization':auth}
            )
        if result.status_code == 200:
            bk=result.content
        if bk.find("true"):
            pass
            print "sina,"
        else:
            return False
    except:
        return traceback.print_exc()

def send_sina_web_msgs(username,password,msg):
        # send sina msgs. use sina username, password.
        # the msgs parameter is a message list, not a single string.       
        result = urlfetch.fetch(url="https://login.sina.com.cn/sso/login.php?username=%s&password=%s&returntype=TEXT"%(username,password))
        cookie = Cookie.SimpleCookie(result.headers.get('set-cookie', ''))
        msg=unescape(msg)
        form_fields = {
          "content": msg,          
        }
        form_data = urllib.urlencode(form_fields)

        result = urlfetch.fetch(url="http://t.sina.com.cn/mblog/publish.php",
                            payload=form_data,
                            method=urlfetch.POST,
                            headers={'Referer':'http://t.sina.com.cn','Cookie' : make_cookie_header(cookie)})
        #print ""
        #print result.content
        
def send_163_msgs(username,password,msg):
        # send sina msgs. use sina username, password.
        # the msgs parameter is a message list, not a single string.       
        result = urlfetch.fetch(url="https://reg.163.com/logins.jsp?username=%s&password=%s&product=t&type=1"%(username,password))
        cookie = Cookie.SimpleCookie(result.headers.get('set-cookie', ''))
        msg=unescape(msg)
        form_fields = {
          "status": msg,          
        }
        form_data = urllib.urlencode(form_fields)

        result = urlfetch.fetch(url="http://t.163.com/statuses/update.do",
                            payload=form_data,
                            method=urlfetch.POST,
                            headers={'Referer':'http://t.163.com','Cookie' : make_cookie_header(cookie)})
        #print ""
        #print result.content
        
def send_sohu_msgs(username,password,msg):
	auth=base64.b64encode(username+":"+password)
	auth='Basic '+auth
	msg=unescape(msg)
	form_fields = {
			"status": msg,
			}
	form_data = urllib.urlencode(form_fields)
	result = urlfetch.fetch(url="http://api.t.sohu.com/statuses/update.xml",
			payload=form_data,
			method=urlfetch.POST,
			headers={'Authorization':auth}
			)
	if result.status_code == 200:
		bk=result.content
		if bk.find("true"):
			return True
	else:
		return False

def send_fanfou_msgs(username,password,msg):
	auth=base64.b64encode(username+":"+password)
	auth='Basic '+auth
	msg=unescape(msg)
	form_fields = {
			"status": msg,
			}
	form_data = urllib.urlencode(form_fields)
	result = urlfetch.fetch(url="http://api.fanfou.com/statuses/update.xml",
			payload=form_data,
			method=urlfetch.POST,
			headers={'Authorization':auth}
			)
	if result.status_code == 200:
		bk=result.content
		if bk.find("true"):
			return True
	else:
		return False

def send_digu_msgs(username,password,msg):
	auth=base64.b64encode(username+":"+password)
	auth='Basic '+auth
	msg=unescape(msg)
	form_fields = {
			"content": msg,
			}
	form_data = urllib.urlencode(form_fields)
	result = urlfetch.fetch(url="http://api.minicloud.com.cn/statuses/update.format",
			payload=form_data,
			method=urlfetch.POST,
			headers={'Authorization':auth}
			)
	if result.status_code == 200:
		bk=result.content
		if bk.find("true"):
			return True
	else:
		return False
    
def send_9911_msgs(username,password,msg):
	auth=base64.b64encode(username+":"+password)
	auth='Basic '+auth
	msg=unescape(msg)
	form_fields = {
			"status": msg,
			}
	form_data = urllib.urlencode(form_fields)
	result = urlfetch.fetch(url="http://api.9911.com/statuses/update.xml",
			payload=form_data,
			method=urlfetch.POST,
			headers={'Authorization':auth}
			)
	if result.status_code == 200:
		bk=result.content
		if bk.find("true"):
			return True
	else:
		return False

def send_zuosa_msgs(username,password,msg):
	auth=base64.b64encode(username+":"+password)
	auth='Basic '+auth
	msg=unescape(msg)
	form_fields = {
			"status": msg,
			}
	form_data = urllib.urlencode(form_fields)
	result = urlfetch.fetch(url="http://api.zuosa.com/statuses/update.xml",
			payload=form_data,
			method=urlfetch.POST,
			headers={'Authorization':auth}
			)
	if result.status_code == 200:
		bk=result.content
		if bk.find("true"):
			return True
	else:
		return False

def send_renjian_msgs(username,password,msg):
	auth=base64.b64encode(username+":"+password)
	auth='Basic '+auth
	msg=unescape(msg)
	form_fields = {
			"text": msg,
			}
	form_data = urllib.urlencode(form_fields)
	result = urlfetch.fetch(url="http://api.renjian.com/statuses/update.xml",
			payload=form_data,
			method=urlfetch.POST,
			headers={'Authorization':auth}
			)
	if result.status_code == 200:
		bk=result.content
		if bk.find("true"):
			return True
	else:
		return False

def send_follow5_msgs(username,password,msg):
	auth=base64.b64encode(username+":"+password)
	auth='Basic '+auth
	msg=unescape(msg)
	form_fields = {
			"status": msg,
			}
	form_data = urllib.urlencode(form_fields)
	result = urlfetch.fetch(url="http://api.follow5.com/api/statuses/update.xml?api_key=9E76EE7693D280446FB6CA4A30754ED8",
			payload=form_data,
			method=urlfetch.POST,
			headers={'Authorization':auth}
			)
	if result.status_code == 200:
		bk=result.content
		if bk.find("true"):
			return True
	else:
		return False

def send_pingfm_msgs(api_key,user_app_key,msg):
	msg=unescape(msg)
	form_fields = {
			"api_key": api_key,
			"user_app_key": user_app_key,
			"post_method": "default",
			"body": msg,
			}
	form_data = urllib.urlencode(form_fields)
	result = urlfetch.fetch(url="http://api.ping.fm/v1/user.post",
			payload=form_data,
			method=urlfetch.POST
			)
	if result.status_code == 200:
		bk=result.content
		if bk.find("true"):
			return True
	else:
		return False

def send_hellotxt_msgs(user_key,app_key,msg):
	msg=unescape(msg)
	form_fields = {
			"user_key": user_key,
			"app_key": app_key,
			"body": msg,
			}
	form_data = urllib.urlencode(form_fields)
	result = urlfetch.fetch(url="http://hellotxt.com/api/v1/method/user.post",
			payload=form_data,
			method=urlfetch.POST
			)
	if result.status_code == 200:
		bk=result.content
		if bk.find("true"):
			return True
	else:
		return False

def send_wbto_msgs(username,password,msg):
	auth=base64.b64encode(username+":"+password)
	auth='Basic '+auth
	msg=unescape(msg)
	form_fields = {
			"content": msg,
			}
	form_data = urllib.urlencode(form_fields)
	result = urlfetch.fetch(url="http://wbto.cn/api/update.xml?source=key",
			payload=form_data,
			method=urlfetch.POST,
			headers={'Authorization':auth}
			)
	if result.status_code == 200:
		bk=result.content
		if bk.find("true"):
			return True
	else:
		return False

def strip_tags(html):
    from HTMLParser import HTMLParser
    html=html.strip()
    html=html.strip("\n")
    result=[]
    parse=HTMLParser()
    parse.handle_data=result.append
    parse.feed(html)
    parse.close()
    return "".join(result)
#get one page of to user's replies, 20 messages at most. 
def parseTwitter(twitter_id,since_id="",):
    salt = "".join(random.sample("abcdefghijklmnopqrstuvwxyz",6))
    url="https://twitter.com/%s?%s"%(twitter_id,salt)
    result = urllib2.urlopen( url ).read()
#    result = urlfetch.fetch(url,deadline=10)
    if result:#.status_code == 200:
        content=result#.content
        m= re.findall(r'(?i)<a href="/%s/status/(\d+?)"[\s\S]*?<p class="js-tweet-text">\s+(?!@)(.+?)\s+</p>'%twitter_id, content)
        print "<html><body><ol>"
        no_sync = []
        for status in m:
            id=status[0]
            if id == since_id:
                break
            else:
                if status[1].find('@',1) != -1:
                    pass
                else:
                    no_sync.append(status)
    else:
        print "get twitter data error. "
        print result#.content
    return no_sync

def sendpost(no_sync,config):
        for x in reversed(no_sync):
            id=x[0]
            text=strip_tags(x[1])
            truelink = lambda reobj:reobj.group(0)[:-4]+" "
            text = re.sub(r'http://\S+… ', truelink, text)
            print "<li>",id,text,"</li>"
            
            ret = {}
            print "sync to: "
            if "" != config.get('plurk','username'):
                ret["plurk"] = send_plurk_msgs(config.get('plurk','username'), config.get('plurk','password'),text)
            if "" != config.get('sina','username'):
                ret["sina"] = send_sina_msgs(config.get('sina','username'), config.get('sina','password'),text)
            if "" != config.get('163','username'):
                ret["163"] = send_163_msgs(config.get('163','username'), config.get('163','password'),text)
            if "" != config.get('sohu','username'):
                ret["sohu"] = send_sohu_msgs(config.get('sohu','username'), config.get('sohu','password'),text)
            if "" != config.get('fanfou','username'):
                ret["fanfou"] = send_fanfou_msgs(config.get('fanfou','username'), config.get('fanfou','password'),text)
            if "" != config.get('9911','username'):
                ret["9911"] = send_9911_msgs(config.get('9911','username'), config.get('9911','password'),text)
            if "" != config.get('zuosa','username'):
                ret["zuosa"] = send_zuosa_msgs(config.get('zuosa','username'), config.get('zuosa','password'),text)
            if "" != config.get('renjian','username'):
                ret["renjian"] = send_renjian_msgs(config.get('renjian','username'), config.get('renjian','password'),text)
            if "" != config.get('follow5','username'):
                ret["follow5"] = send_follow5_msgs(config.get('follow5','username'), config.get('follow5','password'),text)
            if "" != config.get('pingfm','api_key'):
                ret["pingfm"] = send_pingfm_msgs(config.get('pingfm','api_key'), config.get('pingfm','user_app_key'),text)
            if "" != config.get('hellotxt','username'):
                ret["hellotxt"] = send_hellotxt_msgs(config.get('hellotxt','username'), config.get('hellotxt','password'),text)
            if "" != config.get('wbto','username'):
                ret["wbto"] = send_wbto_msgs(config.get('wbto','username'), config.get('wbto','password'),text)
            print "<br />\n"
            msg=Twitter()
            msg.id=id
            msg.put()
            for key in ret:
                if ret[key]:
                    print "<p>%s sync failure</p>"%key
                    #raise Exception,ret[key]
        print "</ol></body></html>"
        
print ""
latest=getLatest() 
deleteData(since_id=latest)

config=ConfigParser.ConfigParser()
config.read('config.ini')

res_type = config.get('res','type')
username = config.get('res','username')
if res_type == "twitter":
    sendpost(parseTwitter(twitter_id=username,since_id=latest),config)

else:
    print "Unsupport resource type '%s'"%res_type
