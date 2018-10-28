#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import http.client
import re
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

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)
    
    
def list_bounds():
  
  config.read('pygmap3.cfg')
  os.chdir(WORK_DIR + "precomp")
  
  print()
  printinfo("local files:")
  for i in ['sea', 'bounds']:
    print()
    list_zip = [x for x in os.listdir() if x.startswith(i) if x.endswith(".zip")]
    list_zip = sorted(list_zip, reverse=True)
    for i in list_zip: 
      print(i)
  print()  

  www = "osm.thkukuk.de"
  path =  "/data/"
  
  printinfo("files on thkukuk.de (*-latest not listed):")
  for i in ['sea', 'bounds']:
    print()
    try:
      target = http.client.HTTPConnection(www)
      target.request("GET", (path))
      htmlcontent =  target.getresponse()
      data = htmlcontent.read()
      data = data.decode('utf8')
      if i == "bounds":
        pattern = re.compile('bounds-20\d{6}.zip')
      elif i == "sea":
        pattern = re.compile('sea-20\d{12}.zip')
      target.close()
        
      list = sorted(pattern.findall(data), reverse=True)
      list_new = []
      for i in list:
        if i not in list_new:
          list_new.append(i)
      for i in list_new:   
        print(i)      

    except:
      
      printerror("Oops, something went wrong, while trying to get the versions on the thkukuk.de")

  print()  

def latest_bounds():
  
  config.read('pygmap3.cfg')
  os.chdir(WORK_DIR + "precomp")
  
  for i in ['sea', 'bounds']:
    
    www = "osm.thkukuk.de"
    path =  "/data/"
    url = "http://" + www + path + i + "-latest.zip"
    file_name = i + "-latest.zip"    

    try:
      print()
      if os.path.exists(file_name):
        os.remove(file_name)
      printinfo("download " + url)
      print()
      with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    except:
      print()
      printerror("failed download " + url)
      print()
      break

  os.chdir(WORK_DIR)

def fetch_bounds():
  
  config.read('pygmap3.cfg')
  os.chdir(WORK_DIR + "precomp")
  
  for i in ['sea', 'bounds']:
    if config['bounds'][i] != i + "-latest.zip":
    
      www = "osm.thkukuk.de"
      path =  "/data/"
      file_name = config['bounds'][i]
      url = "http://" + www + path + file_name      
      
      if os.path.exists(file_name):
        printinfo("file exists:  " + file_name)
        print()
      else:
        try:
          print()
          printinfo("download " + url)
          print()
          with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        except:
          print()
          printerror("failed download:  " + url)
          print()
          break

  os.chdir(WORK_DIR)
