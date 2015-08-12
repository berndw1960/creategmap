#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import http.client
import re
import tarfile
import configparser
import urllib.request
import shutil
import time


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

def from_mkgmap_org():
  config.read('pygmap3.cfg')

  use_mkgmap_test = config['runtime']['use_mkgmap_test']

  for i in ['splitter', 'mkgmap']:
    try:

      target = http.client.HTTPConnection("www.mkgmap.org.uk")
      target.request("GET", "/download/" + i + ".html")
      htmlcontent =  target.getresponse()
      data = htmlcontent.read()
      data = data.decode('utf8')

      if use_mkgmap_test == "yes" and i == "mkgmap":

        mkgmap_test = config['runtime']['mkgmap_test']

        pattern = re.compile("mkgmap-" + mkgmap_test + "-r\d{4}.zip")
        i_rev_pre = sorted(pattern.findall(data), reverse=True)[0]
        i_rev = os.path.splitext(os.path.basename(i_rev_pre))[0]

      else:

        if i == "splitter":
          #pattern = re.compile('/download/splitter-r\d{3}.zip')
          pattern = re.compile('splitter-r\d{3}.zip')
        elif i == "mkgmap":
          #pattern = re.compile('/download/mkgmap-r\d{4}.zip')
          pattern = re.compile('mkgmap-r\d{4}.zip')

        i_rev_pre = sorted(pattern.findall(data), reverse=True)[0]
        i_rev = os.path.splitext(os.path.basename(i_rev_pre))[0]

        #i_rev.replace("/download/", "")

      target.close()

    except:
      print()
      printwarning("can't get a new " + i + "-rev from mkgmap.org")
      printwarning("trying to use another one")
      print()

      try:
        i_rev = config['runtime'][i]
      except:
        print()
        printerror(i + "_rev not set in config")
        printerror("i don't know, which version should i use!")
        print()
        quit()

    if os.path.exists(i_rev) == False:
      if os.path.isfile(i_rev + ".tar.gz") == True:
        try:
          tar = tarfile.open((i_rev) + ".tar.gz")
          tar.extractall()
          tar.close()

        except:
          print()
          printerror(" couldn't extract " + i_rev + " from local file")
          print()
          quit()

      else:
        try:
          url = "http://www.mkgmap.org.uk/download/" + i_rev + ".tar.gz"
          file_name = i_rev + ".tar.gz"
          print()
          printinfo("download " + url)

          # Download the file from `url` and save it locally under `file_name`:
          with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

          try:
            tar = tarfile.open((i_rev) + ".tar.gz")
            tar.extractall()
            tar.close()

          except:
            print()
            printerror(" couldn't extract " + i_rev)
            print()
            quit()

        except:
          print()
          printerror("failed download " + i_rev + ".tar.gz")
          print()
          quit()

    if os.path.exists(i_rev) == False:
      print()
      printerror(i_rev + " didn't exist")
      print()
      quit()

    if use_mkgmap_test == "yes" and i == "mkgmap":
      print()
      printinfo("using " + i_rev)

    config.set('runtime', i, i_rev)
    write_config()

