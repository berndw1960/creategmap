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
  

"""
  get splitter and mkgmap 
  
"""  

WORK_DIR = os.environ['HOME'] + "/map_build/"

config = configparser.ConfigParser()


def get_tools():
  
  target = http.client.HTTPConnection("www.mkgmap.org.uk")
  config.read('pygmap3.cfg') 
  global splitter
  if config.get('splitter', 'version') != "latest":
    ExitCode = os.path.exists("splitter-" + (config.get('splitter', 'version')))
    if ExitCode == False:
      os.system(("wget -N http://www.mkgmap.org.uk/download/splitter-") + 
	        (config.get('splitter', 'version')) + (".tar.gz"))
      tar = tarfile.open("splitter-" + (config.get('splitter', 'version')) + ".tar.gz")
      tar.extractall()
      tar.close()
      
    splitter = (WORK_DIR) + "splitter-" + (config.get('splitter', 'version')) + "/splitter.jar"
  
  else:    
    target.request("GET", "/download/splitter.html")
    htmlcontent =  target.getresponse()
    print(htmlcontent.status, htmlcontent.reason)
    data = htmlcontent.read()
    data = data.decode('utf8')
    pattern = re.compile('splitter-r\d{3}')
    splitter_rev = sorted(pattern.findall(data), reverse=True)[1]
    target.close()
    os.system("wget -N http://www.mkgmap.org.uk/download/" + 
              (splitter_rev) + ".tar.gz")
    tar = tarfile.open((splitter_rev) + ".tar.gz")
    tar.extractall()
    tar.close()
    
    splitter = (WORK_DIR) + (splitter_rev) + "/splitter.jar"
    
    
  global mkgmap  
  if config.get('mkgmap', 'version') != "latest":
    ExitCode = os.path.exists("mkgmap-" + (config.get('mkgmap', 'version')))
    if ExitCode == False:
      os.system("wget -N http://www.mkgmap.org.uk/download/mkgmap-" + 
                (config.get('mkgmap', 'version')) + ".tar.gz")
      tar = tarfile.open("mkgmap-" + (config.get('mkgmap', 'version')) + ".tar.gz")
      tar.extractall()
      tar.close()
      
      mkgmap = (WORK_DIR) + "mkgmap-" + (config.get('mkgmap', 'version')) + "/mkgmap.jar"
  else:
    target.request("GET", "/download/mkgmap.html")
    htmlcontent =  target.getresponse()
    print(htmlcontent.status, htmlcontent.reason)
    data = htmlcontent.read()
    data = data.decode('utf8')
    pattern = re.compile('mkgmap-r\d{4}')
    mkgmap_rev = sorted(pattern.findall(data), reverse=True)[1]
    target.close()
    os.system("wget -N http://www.mkgmap.org.uk/download/" + 
              (mkgmap_rev) + (".tar.gz"))
    tar = tarfile.open((mkgmap_rev) + ".tar.gz")
    tar.extractall()
    tar.close()
    
    mkgmap = (WORK_DIR) + (mkgmap_rev) + "/mkgmap.jar"

  target.close()
  
  
def split():
  
  config.read('pygmap3.cfg') 
  buildmap = config.get('runtime', 'buildmap')
  
  datei = open((WORK_DIR) + "tiles/" + (buildmap) + "_split.lck", "w")
  datei.close()
  
  java_opts = ("java -ea " + (config.get('DEFAULT', 'ramsize')) + " -jar " + (splitter))
  
  splitter_opts = (" --geonames-file=" + (WORK_DIR) + "cities15000.zip " +
                 " --mapid=" + (config.get('DEFAULT', 'mapid')) + "0001 " +
                 " --output=o5m " +
                 " --keep-complete " +
                 " --write-kml=" + (buildmap) + ".kml "
                 " --max-nodes=" + (config.get('splitter', 'maxnodes')) + 
                 " --overlap=0 ")
  areas_list = (" --split-file=" + (WORK_DIR) + "areas/" + (buildmap) + "_areas.list ")
  
  BUILD_O5M = ((WORK_DIR) + "o5m/" + (buildmap) + ".o5m")
  
  map_data = (BUILD_O5M)
  
  ExitCode = os.path.exists((WORK_DIR) + "areas/" + (buildmap) + "_areas.list")
  if ExitCode == True:
    os.chdir((WORK_DIR) + "tiles")
    os.system((java_opts) + (splitter_opts) + (areas_list) + (map_data))
  else:
    os.chdir((WORK_DIR) + "tiles")
    os.system((java_opts) + (splitter_opts) + (map_data))
    os.system("cp areas.list " + (WORK_DIR) + "/areas/" + (buildmap) + "_areas.list")
  
  ExitCode = os.path.exists((WORK_DIR) + "tiles/template.args")
  if ExitCode == True:
    datei = open((WORK_DIR) + "tiles/" + (buildmap) + "_split.ready", "w")
    datei.close()
  else:
    printerror("Splitter-Error!")
    quit()
  os.remove((WORK_DIR) + "tiles/" + (buildmap) + "_split.lck")



 
""" 
 create the layers 
 add your own styles in mystyles
"""

def style():
  config.read('pygmap3.cfg') 
  ExitCode = os.path.exists((WORK_DIR) + "mystyles/" + (layer) + "_style")
  global mapstyle
  if ExitCode == True:
    mapstyle = "mystyles"
  else:
    ExitCode = os.path.exists((WORK_DIR) + "aiostyles")
    if ExitCode == False:
      os.system("wget -N http://dev.openstreetmap.de/aio/aiostyles.7z")
      os.system("7z x aiostyles.7z -oaiostyles")
    mapstyle = "aiostyles"
    
  ExitCode = os.path.exists((mapstyle) + "/" + (layer) + "_typ.txt") 
  if ExitCode == False:
    printerror(" Please convert " +
        (mapstyle) + "/" + (layer) + ".TYP to " + (layer) + "_typ.txt!")
    quit()  

  
def mkgmap_java():
  config.read('pygmap3.cfg') 
  buildmap = config.get('runtime', 'buildmap')
  buildday = config.get('runtime', 'buildday')
  os.system("java -ea " + (config.get('DEFAULT', 'ramsize')) + 
            " -Dlog.config=" + (WORK_DIR) + "log.conf " +
            " -jar " + (mkgmap) + 
            " -c "  + (WORK_DIR) + (config.get((layer), 'conf')) +
            " --style-file=" + (WORK_DIR) + (mapstyle) + "/" + (layer) + "_style " +
            " --bounds=" + (WORK_DIR) +"bounds.zip " +
            " --mapname=" + (config.get('DEFAULT', 'mapid')) + (config.get((layer), 'mapid_ext')) +
            " --family-id=" + (config.get((layer), 'family-id')) +
            " --product-id=" + (config.get((layer), 'product-id')) +
            " --description=" + (buildday) +
            " --family-name=" + (config.get((layer), 'family-name')) +
            " --draw-priority=" + (config.get((layer), 'draw-priority')) + " " +
            (WORK_DIR) + "tiles/*.o5m " + 
            (WORK_DIR) + (mapstyle) + "/" + (layer) + "_typ.txt")

def mkgmap_render():
  config.read('pygmap3.cfg') 
  buildmap = config.get('runtime', 'buildmap')
  buildday = config.get('runtime', 'buildday')
  global layer
  for layer in ['basemap', 'rrk', 'fixme']:
    build = config.get((layer), 'build')
    if build == "yes":
      os.chdir(WORK_DIR)
      style()

      path = ((WORK_DIR) + (layer)) 
      for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):

          try:
            os.remove(os.path.join(path, file))
          except:
            print('Could not delete', file, 'in', path)
      
      os.chdir(path)     
      printinfo("entered " + os.getcwd())
      printinfo("Now building " + (layer) + "-layer with " + (mapstyle)) 
     
      mkgmap_java()
      
      unzip_dir = ((WORK_DIR) + "gps_ready/unzipped/" + (buildday) + "/")
      
      os.system("cp gmapsupp.img " + (unzip_dir) + (buildmap) + "_" + (layer) + "_gmapsupp.img")
           
      log_dir = ((WORK_DIR) + "log/" + (buildday) + "/" + (layer) + "/") 
    
      ExitCode = os.path.exists(log_dir)
      if ExitCode == True:
        path = (log_dir) 
        for file in os.listdir(path):
          if os.path.isfile(os.path.join(path, file)):
            try:
              os.remove(os.path.join(path, file))
            except:
              print('Could not delete', file, 'in', path)
              
      elif ExitCode == False:
        os.makedirs(log_dir)

      ExitCode = os.path.exists("mkgmap.log.0")
      if ExitCode == True:
        os.system("mv mkgmap.log.* " + (log_dir))
