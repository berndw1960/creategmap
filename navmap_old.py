#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import http.client
import re
import tarfile
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

config = configparser.ConfigParser()

def pre_comp():

  config.read('pygmap3.cfg')

  """
  boundaries from osm2.pleiades.uni-wuppertal.de
  """

  if config.get('navmap', 'pre_comp') == "yes":
    if config.get('navmap', 'sea') == "latest":
      target = http.client.HTTPConnection("osm2.pleiades.uni-wuppertal.de")
      target.request("GET", "/sea/")
      htmlcontent =  target.getresponse()
      data = htmlcontent.read()
      data = data.decode('utf8')
      pattern = re.compile('201\d{5}')
      sea_date = sorted(pattern.findall(data), reverse=True)[1]
      sea_rev = "sea_" + (sea_date)
      target.close()
      config.set('navmap', 'sea_rev', (sea_rev))

      ExitCode = os.path.exists((sea_rev) + ".zip")
      if ExitCode == False:
        url = "http://osm2.pleiades.uni-wuppertal.de/sea/" + (sea_date) + "/" + (sea_rev) + ".zip"
        file_name = (sea_rev) + ".zip"

        # Download the file from `url` and save it locally under `file_name`:
        with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
          shutil.copyfileobj(response, out_file)

      ExitCode = os.path.exists((sea_rev) + ".zip")
      if ExitCode == True:
        printinfo("using " + (sea_rev) + ".zip")

      with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)

    else:
      if config.has_option('navmap', 'sea_rev') == True:
        sea_rev = config.get('navmap', 'sea_rev')
        ExitCode = os.path.exists((sea_rev) + ".zip")
        if ExitCode == False:
          config.set('navmap', 'use_sea', 'no',)
          printwarning("use_sea disabled, " + (sea_rev) + ".zip didn't exist")
          with open('pygmap3.cfg', 'w') as configfile:
            config.write(configfile)
        else:
          printinfo("using " + (sea_rev) + ".zip")
      else:
        config.set('navmap', 'use_sea', 'no',)
        printwarning("use_sea disabled, sea_rev isn't set")
        with open('pygmap3.cfg', 'w') as configfile:
          config.write(configfile)

    if config.get('navmap', 'bounds') == "latest":
      target = http.client.HTTPConnection("osm2.pleiades.uni-wuppertal.de")
      target.request("GET", "/bounds/")
      htmlcontent =  target.getresponse()
      data = htmlcontent.read()
      data = data.decode('utf8')
      pattern = re.compile('201\d{5}')
      bounds_date = sorted(pattern.findall(data), reverse=True)[1]
      bounds_rev =  "bounds_" + (bounds_date)
      target.close()

      config.set('navmap', 'bounds_rev', (bounds_rev))

      ExitCode = os.path.exists((bounds_rev) + ".zip")
      if ExitCode == False:
        url = "http://osm2.pleiades.uni-wuppertal.de/bounds/" + (bounds_date) + "/" + (bounds_rev) + ".zip"
        file_name = (bounds_rev) + ".zip"

        # Download the file from `url` and save it locally under `file_name`:
        with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
          shutil.copyfileobj(response, out_file)

      ExitCode = os.path.exists((bounds_rev) + ".zip")
      if ExitCode == True:
        printinfo("using " + (bounds_rev) + ".zip")

      with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)

    else:
      if config.has_option('navmap', 'bounds_rev') == True:
        bounds_rev = config.get('navmap', 'bounds_rev')
        ExitCode = os.path.exists((bounds_rev) + ".zip")
        if ExitCode == False:
          config.set('navmap', 'use_bounds', 'no',)
          printwarning("use_bounds disabled, " + (bounds_rev) + ".zip didn't exist")
          with open('pygmap3.cfg', 'w') as configfile:
            config.write(configfile)
        else:
          printinfo("using " + (bounds_rev) + ".zip")
      else:
        config.set('navmap', 'use_bounds', 'no',)
        printwarning("use_bounds disabled, bounds_rev isn't set")
        with open('pygmap3.cfg', 'w') as configfile:
          config.write(configfile)
  else:
    printwarning("use_bounds in pygmap3.cfg is disabled!")


