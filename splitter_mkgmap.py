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

  config.set('runtime', 'splitter_path', (splitter))
  write_config()


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

  config.set('runtime', 'mkgmap_path', (mkgmap))
  write_config()

  target.close()



"""
split raw-data

"""

def split():

  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')

  datei = open((WORK_DIR) + "tiles/" + (buildmap) + "_split.lck", "w")
  datei.close()

  java_opts = ("java -ea " + (config.get('ramsize', 'ramsize')) + " -jar " + (splitter))

  """
  splitter-options
  """
  splitter_opts = (" --geonames-file=" + (WORK_DIR) + "cities15000.zip " +
                   " --mapid=" + (config.get('mapid', 'mapid')) + "0001 " +
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

  """
  if there is only a TYP-File
  """
  ExitCode = os.path.exists((mapstyle) + "/" + (layer) + "_typ.txt")
  if ExitCode == False:
    printerror(" Please convert " +
        (mapstyle) + "/" + (layer) + ".TYP to " + (layer) + "_typ.txt!")
    quit()


  """
  Test for style-dir and remove old data from there
  """

  ExitCode = os.path.exists((WORK_DIR) + (layer))
  if ExitCode == False:
    os.mkdir((WORK_DIR) + (layer))
  else:
    path = ((WORK_DIR) + (layer))
    for file in os.listdir(path):
      if os.path.isfile(os.path.join(path, file)):
        try:
          os.remove(os.path.join(path, file))
        except:
          print('Could not delete', file, 'in', path)


"""
mkgmap-options
"""

ExitCode = os.path.exists((WORK_DIR) + "precomp_sea")
if ExitCode == False:
  printwarning("No precomp_sea found, get it from navmap.eu ")
  printwarning("example: http://www.navmaps.eu/wanmil/sea_20130205.zip ")
  printwarning("store it extracted as 'precomp_sea' in " + (WORK_DIR))
  option_generate_sea = " --generate-sea: extend-sea-sectors,close-gaps=6000,floodblocker,land-tag=natural=background "
else:
  printinfo("Use '--precomp_sea'! ")
  option_generate_sea = " --precomp-sea=" + (WORK_DIR) +"precomp_sea --generate-sea "



def mkgmap_java():
  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')
  buildday = config.get('runtime', 'buildday')
  os.system("java -ea " + (config.get('ramsize', 'ramsize')) +
            " -Dlog.config=" + (WORK_DIR) + "log.conf " +
            " -jar " + (mkgmap) +
            " -c "  + (WORK_DIR) + (config.get((layer), 'conf')) +
            " --style-file=" + (WORK_DIR) + (mapstyle) + "/" + (layer) + "_style " +
            " --bounds=" + (WORK_DIR) +"bounds.zip " +
            (option_generate_sea) +
            " --mapname=" + (config.get('mapid', 'mapid')) + (config.get((layer), 'mapid_ext')) +
            " --family-id=" + (config.get((layer), 'family-id')) +
            " --product-id=" + (config.get((layer), 'product-id')) +
            " --description=" + (buildday) +
            " --family-name=" + (config.get((layer), 'family-name')) +
            " --draw-priority=" + (config.get((layer), 'draw-priority')) + " " +
            (WORK_DIR) + "tiles/*.o5m " +
            (WORK_DIR) + (mapstyle) + "/" + (layer) + "_typ.txt")


"""
map-rendering
"""

def mkgmap_render():
  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')
  buildday = config.get('runtime', 'buildday')
  global layer
  for layer in config['map_styles']:
    build = (config['map_styles'][(layer)])
    if build == "yes":
      os.chdir(WORK_DIR)
      style()

      os.chdir(layer)
      printinfo("entered " + os.getcwd())
      printinfo("Now building " + (layer) + "-layer with " + (mapstyle))

      mkgmap_java()

      """
      mv the ready gmapsupp.img to destination (unzip_dir) and
      rename it to (buildmap)_gmapsupp.img
      """

      unzip_dir = ((WORK_DIR) + "gps_ready/unzipped/" + (buildday) + "/")

      os.system("cp gmapsupp.img " + (unzip_dir) + (buildmap) + "_" + (layer) + "_gmapsupp.img")

      log_dir = ((WORK_DIR) + "log/" + (buildday) + "/" + (layer) + "/")

      """
      save the mkgmap-log for errors
      """

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
