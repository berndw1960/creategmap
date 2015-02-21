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
  try:
    www_path = "osm2.pleiades.uni-wuppertal.de"
    path =  "/" + (i) + "/"
    target = http.client.HTTPConnection(www_path)
    target.request("GET", (path))
    htmlcontent =  target.getresponse()
    data = htmlcontent.read()
    data = data.decode('utf8')
    pattern = re.compile('201\d{5}')
    date = sorted(pattern.findall(data), reverse=True)[1]
    target.close()

    rev = (i) + "_" + (date)

    if config.has_option('navmap', (i) + "_rev"):
      prerev = config.get('navmap', (i) + "_rev")
      if (prerev) != (rev):
        config.set('navmap', "pre_" + (i) + "_rev", (prerev))

  except:
    if config.has_option('navmap', (i) + "_rev"):
      rev = config.get('navmap', (i) + "_rev")
    else:
      print()
      printerror((i) + "_rev not set in config")
      print()
      quit()

  if config.has_option('navmap', 'use_old_bounds'):
    if config.get('navmap', 'use_old_bounds') == "yes":
      rev = config.get('navmap', "pre_" + (i) + "_rev")

  if os.path.exists((rev) + ".zip") == False:

    try:
      url = "http://" + (www_path) + (path) + (date) + "/" + (i) + "_" + (date) + ".zip"
      file_name = (i) + "_" + (date) + ".zip"
      print()
      printinfo("download " + (url))

      with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    except:
      print()
      printerror("failed download " + (i))
      print()
      quit()

  if os.path.exists((rev) + ".zip") == True:
    config.set('navmap', (i) + "_rev", (rev))
    if config.get('navmap', "use_" + (i)) == "no":
      config.set('navmap', "use_" + (i), 'yes',)
    print()
    printinfo("using " + (rev) + ".zip")
  else:
    if config.get('navmap', "use_" + (i)) == "yes":
      config.set('navmap', "use_" + (i), 'no',)
    print()
    printwarning("pre_comp " + (i) + " disabled, needed file(s) not found")

  write_config()

