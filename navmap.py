#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


WORK_DIR = os.environ['HOME'] + "/map_build/"
config = configparser.ConfigParser()

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

def latest_bounds():
  config.read('pygmap3.cfg')
  os.chdir(WORK_DIR + "precomp")
  
  for i in ['sea', 'bounds']:
    
    www = "osm.thkukuk.de"
    path =  "/data/"

    try:
      url = "http://" + www + path + i + "-latest.zip"
      print()
      printinfo("download " + url)
      os.system("wget " + url)

    except:
      print()
      printerror("failed download " + url)
      print()
      break

  os.chdir(WORK_DIR)

def list_bounds():
  config.read('pygmap3.cfg')
  os.chdir(WORK_DIR + "precomp")
  for i in ['sea', 'bounds']:
    print()
    list_zip = [x for x in os.listdir() if x.startswith(i) if x.endswith(".zip")]
    list_zip = sorted(list_zip, reverse=True)
    for i in list_zip: 
      print(i)
  print()  
    
    
