#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import http.client
import re
import tarfile
import configparser


def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


WORK_DIR = os.environ['HOME'] + "/map_build/"

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
    pattern = re.compile('splitter-r\d{3}')
    splitter_rev = sorted(pattern.findall(data), reverse=True)[1]
    target.close()

  else:
    splitter_rev = config.get('splitter', 'version')


  ExitCode = os.path.exists(splitter_rev)
  if ExitCode == False:
    os.system("wget -N http://www.mkgmap.org.uk/download/" + (splitter_rev) + ".tar.gz")

    tar = tarfile.open((splitter_rev) + ".tar.gz")
    tar.extractall()
    tar.close()

  splitter_path = (WORK_DIR) + (splitter_rev) + "/splitter.jar"

  if config.get('mkgmap', 'latest') == "yes":
    target = http.client.HTTPConnection("www.mkgmap.org.uk")
    target.request("GET", "/download/mkgmap.html")
    htmlcontent =  target.getresponse()
    data = htmlcontent.read()
    data = data.decode('utf8')
    pattern = re.compile('mkgmap-r\d{4}')
    mkgmap_rev = sorted(pattern.findall(data), reverse=True)[1]
    target.close()

  else:
    mkgmap_rev = config.get('mkgmap', 'version')


  ExitCode = os.path.exists(mkgmap_rev)
  if ExitCode == False:
    os.system("wget -N http://www.mkgmap.org.uk/download/" + (mkgmap_rev) + (".tar.gz"))

    tar = tarfile.open((mkgmap_rev) + ".tar.gz")
    tar.extractall()
    tar.close()

  mkgmap_path = (WORK_DIR) + (mkgmap_rev) + "/mkgmap.jar"


  """
  boundaries from navmap.eu
  """

  if config.get('navmap_eu', 'latest') == "yes":
    os.system("wget http://www.navmaps.eu/wanmil/")

    ExitCode = os.path.exists("index.html")
    if ExitCode == True:
      data = open("index.html").readlines()
      data = str(data)
      pattern = re.compile('sea_\d{8}')
      sea_rev = sorted(pattern.findall(data), reverse=True)[1]

  ExitCode = os.path.exists((sea_rev) + (".zip"))
  if ExitCode == False:
    os.system("wget -N http://www.navmaps.eu/wanmil/" + (sea_rev) + (".zip"))

  sea_rev_path = ((WORK_DIR) + (sea_rev) + (".zip"))

  if config.get('navmap_eu', 'latest') == "yes":
    ExitCode = os.path.exists("index.html")
    if ExitCode == True:
      data = open("index.html").readlines()
      data = str(data)
      pattern = re.compile('bounds_\d{8}')
      bounds_rev = sorted(pattern.findall(data), reverse=True)[1]
      os.remove((WORK_DIR) + "index.html")

  ExitCode = os.path.exists((bounds_rev) + (".zip"))
  if ExitCode == False:
    os.system("wget -N http://www.navmaps.eu/wanmil/" + (bounds_rev) + (".zip"))

  bounds_rev_path = ((WORK_DIR) + (bounds_rev) + (".zip"))

  """
  now write  to pygmap3.cfg
  """

  config.set('splitter', 'version', (splitter_rev))
  config.set('runtime', 'splitter_path', (splitter_path))

  config.set('mkgmap', 'version', (mkgmap_rev))
  config.set('runtime', 'mkgmap_path', (mkgmap_path))

  config.set('navmap_eu', 'sea_rev', (sea_rev))
  config.set('runtime', 'sea_rev_path', (sea_rev_path))

  config.set('navmap_eu', 'bounds_rev', (bounds_rev))
  config.set('runtime', 'bounds_rev_path', (bounds_rev_path))

  write_config()

