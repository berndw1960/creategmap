#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import http.client
import re
import tarfile
import configparser
import urllib.request
import shutil


WORK_DIR = os.environ['HOME'] + "/map_build/"


def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)

config = configparser.ConfigParser()

"""
config writer
"""

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

def tar_extract():
  tar = tarfile.open((i_rev) + ".tar.gz")
  tar.extractall()
  tar.close()
  
"""
get splitter and mkgmap

"""


for i in ['splitter', 'mkgmap']:
  config.read('pygmap3.cfg')
  try:
    target = http.client.HTTPConnection("www.mkgmap.org.uk")
    target.request("GET", "/download/" + (i) + ".html")
    htmlcontent =  target.getresponse()
    data = htmlcontent.read()
    data = data.decode('utf8')
    if (i) == "splitter":
      pattern = re.compile('splitter-r\d{3}.zip')
    elif (i) == "mkgmap":
      pattern = re.compile('mkgmap-r\d{4}.zip')
    i_rev_pre = sorted(pattern.findall(data), reverse=True)[0]
    i_rev = os.path.splitext(os.path.basename(i_rev_pre))[0]
    target.close()
    config.set((i), 'version', (i_rev))
    write_config()

  except:
    if config.has_option((i), 'version'):
      i_rev = config.get((i), 'version')
    else:
      print("")
      printerror((i) + "_rev not set in config")
      print("")
      quit() 

  ExitCode = os.path.exists(i_rev)
  if ExitCode == True:
    printinfo("using " + (i_rev))
  else:  
    ExitCode = os.path.isfile((i_rev) + ".tar.gz")
    if ExitCode == True:
      try:
        tar_extract()
      except:
        printerror(" couldn't extract " + (i_rev) + " from local file")
        quit()
        
    else:  
      try:
        url = "http://www.mkgmap.org.uk/download/" + (i_rev) + ".tar.gz"
        file_name = (i_rev) + ".tar.gz"
        print("")
        printinfo("download " + (url))
        print("")
        # Download the file from `url` and save it locally under `file_name`:
        with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
          shutil.copyfileobj(response, out_file)
          
        try:
          tar_extract()
        except:
          printerror(" couldn't extract " + (i_rev) + " from downloaded file")
          quit()
        
      except:
        print("")
        printerror("failed download " + (i_rev) + ".tar.gz")
        print("")
        quit()
    
  ExitCode = os.path.exists(i_rev)
  if ExitCode == False:
    print("")
    printerror((i_rev) + " didn't exist")
    print("")
    quit()     

"""
get the geonames for splitter

"""

ExitCode = os.path.exists((WORK_DIR) + "cities15000.zip")
if ExitCode == False:
  try:
    url = "http://download.geonames.org/export/dump/cities15000.zip"
    file_name = "cities15000.zip"
    print("")
    printinfo("download " + (url))
    print("")
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
      shutil.copyfileobj(response, out_file)
  except:
    print("")
    printerror("failed download cities15000.zip")
    print("")
    quit()    



