#!/usr/bin/env python

###########################################
# create image databases 
# this script query google image search via APIs 
# it requires Tor to be installed.
# author federico.corradi@inilabs.com
##########################################

import json
import os
import time
import requests
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError
import socks
import socket
import mechanize
from mechanize import Browser
from TorCtl import TorCtl
import urllib2
 
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent}


temp = socket.socket #use this to connect to tor configuration port witout proxy since its local machine

def change_identity():
  conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051, passphrase="pubbeti6")
  conn.send_signal("NEWNYM")
  conn.close()

socket.socket=temp 
change_identity()

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, "127.0.0.1", 9050, True)
socket.socket = socks.socksocket

print "new ip-> ", urllib2.urlopen('http://icanhazip.com').read()


def go(query, path, number, tot_pages = 1000):
  """Download full size images from Google image search.
  Don't print or republish images without permission.
  I used this to train a learning algorithm.
  """

  start = 0 # Google's start query string parameter for pagination.
  while start < tot_pages: # Google will only return a max of 56 results.

    if(start % 10 == 0):
      socket.socket=temp
      change_identity()
      socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, "127.0.0.1", 9050, True)
      socket.socket = socks.socksocket
      print "new ip-> ", urllib2.urlopen('http://icanhazip.com').read()
    
    userip = urllib2.urlopen('http://icanhazip.com').read()

    BASE_URL = "https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + query + "&userip=" + userip + "&rsz=8&start=" + str(start) 

    print "BASE URL-> " + BASE_URL

    BASE_PATH = os.path.join(path, query)

    if not os.path.exists(BASE_PATH):
      os.makedirs(BASE_PATH)

    r = requests.get(BASE_URL)# % start)
    start += 8 # 4 images per page.
    try:
        for image_info in json.loads(r.text)['responseData']['results']:
          url = image_info['unescapedUrl']
          try:
            image_r = requests.get(url)
          except ConnectionError, e:
            print 'could not download %s' % url
            continue

          # Remove file-system path characters from name.
          title = image_info['titleNoFormatting'].replace('/', '').replace('\\', '')

          file = open(os.path.join(BASE_PATH, '%s.jpg') % title, 'w')
          try:
            Image.open(StringIO(image_r.content)).save(file, 'JPEG')
          except IOError, e:
            # Throw away some gifs...blegh.
            print 'could not save %s' % url
            continue
          finally:
            file.close()
    except (AttributeError, TypeError, NameError):
        pass
    print start
    
    # Be nice to Google and they'll be nice back :)
    time.sleep(1.5)


### change this line
database_dir = '/home/federico/iniLabs/data/img_db/data/images/'
file_keywords = 'keywords_img.txt'
start_index = 0

with open(file_keywords, 'r') as f:
    for line in f:
        line = line.strip()
        print line
        if(len(line) > 3):
            go(line, database_dir+line+'s', start_index)



