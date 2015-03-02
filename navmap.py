#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import http.client
import re
import configparser
import urllib.request
import shutil

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


WORK_DIR = os.environ['HOME'] + "/map_build/"

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

config = configparser.ConfigParser()
config.read('pygmap3.cfg')

for i in ['sea', 'bounds']:

  www = "osm2.pleiades.uni-wuppertal.de"
  path =  "/" + (i) + "/"

  try:
    target = http.client.HTTPConnection(www)
    target.request("GET", (path))
    htmlcontent =  target.getresponse()
    data = htmlcontent.read()
    data = data.decode('utf8')
    pattern = re.compile('201\d{5}')
    date_new = sorted(pattern.findall(data), reverse=True)[1]
    date_pre = sorted(pattern.findall(data), reverse=True)[2]
    target.close()

  except:
    print()
    printerror("Oops, something went wrong, while trying to get the versions of " + i + "*.zip")
    print()
    break

  if config['navmap']['use_old_bounds'] == "yes":
    date = date_pre
  else:
    date = date_new

  file = i + "_" + date + ".zip"

  if os.path.exists(file) == False:

    try:
      url = "http://" + www + path + date + "/" + file
      print()
      printinfo("download " + url)

      with urllib.request.urlopen(url) as response, open(file, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    except:
      print()
      printerror("failed download " + file)
      print()
      break

write_config()


