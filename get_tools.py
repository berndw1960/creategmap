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

"""
get splitter and mkgmap

"""

def get_tools():

  config.read('pygmap3.cfg')

  if config.get('splitter', 'latest') == "yes":
    target = http.client.HTTPConnection("www.mkgmap.org.uk")
    target.request("GET", "/download/splitter.html")
    htmlcontent =  target.getresponse()
    data = htmlcontent.read()
    data = data.decode('utf8')
    pattern = re.compile('splitter-r\d{3}.zip')
    splitter_rev_pre = sorted(pattern.findall(data), reverse=True)[1]
    splitter_rev = os.path.splitext(os.path.basename(splitter_rev_pre))[0]
    target.close()

  else:
    splitter_rev = config.get('splitter', 'version')


  ExitCode = os.path.exists(splitter_rev)
  if ExitCode == False:
    ExitCode = os.path.isfile((splitter_rev) + ".tar.gz")
    if ExitCode == False:
      url = "http://www.mkgmap.org.uk/download/" + (splitter_rev) + ".tar.gz"
      file_name = (splitter_rev) + ".tar.gz"

      # Download the file from `url` and save it locally under `file_name`:
      with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    tar = tarfile.open((splitter_rev) + ".tar.gz")
    tar.extractall()
    tar.close()

  splitter_path = (WORK_DIR) + (splitter_rev) + "/splitter.jar"
  
  printinfo("using " + (splitter_rev))

  if config.get('mkgmap', 'latest') == "yes":
    target = http.client.HTTPConnection("www.mkgmap.org.uk")
    target.request("GET", "/download/mkgmap.html")
    htmlcontent =  target.getresponse()
    data = htmlcontent.read()
    data = data.decode('utf8')
    pattern = re.compile('mkgmap-r\d{4}.zip')
    mkgmap_rev_pre = sorted(pattern.findall(data), reverse=True)[1]
    mkgmap_rev = os.path.splitext(os.path.basename(mkgmap_rev_pre))[0]
    target.close()

  else:
    mkgmap_rev = config.get('mkgmap', 'version')


  ExitCode = os.path.exists(mkgmap_rev)
  if ExitCode == False:
    ExitCode = os.path.isfile((mkgmap_rev) + ".tar.gz")
    if ExitCode == False:
      url = "http://www.mkgmap.org.uk/download/" + (mkgmap_rev) + ".tar.gz"
      file_name = (mkgmap_rev) + ".tar.gz"

      # Download the file from `url` and save it locally under `file_name`:
      with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    tar = tarfile.open((mkgmap_rev) + ".tar.gz")
    tar.extractall()
    tar.close()

  mkgmap_path = (WORK_DIR) + (mkgmap_rev) + "/mkgmap.jar"


  printinfo("using " + (mkgmap_rev))

  """
  now write to pygmap3.cfg
  """

  config.set('splitter', 'version', (splitter_rev))
  config.set('mkgmap', 'version', (mkgmap_rev))

  write_config()

