#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import mkgmap_download

"""
  split rawdata
  
"""

WORK_DIR = (os.environ['HOME'] + "/map_build/")
config = configparser.ConfigParser()
config.read((WORK_DIR) + 'pygmap3.cfg')

def split():         
  os.chdir(WORK_DIR)
  datei = open((WORK_DIR) + "tiles/" + (config.get('DEFAULT', 'buildmap')) + "_split.lck", "w")
  datei.close()  
  java_opts = ("java -ea " + (config.get('DEFAULT', 'ramsize')) + " -jar " + (splitter))
  splitter_opts = (" --geonames-file=" + (WORK_DIR) + "cities15000.zip " +
                 " --mapid=" + (config.get('DEFAULT', 'mapid')) + "0001 " +
                 " --output=o5m " +
                 " --keep-complete " +
                 " --write-kml=" + (config.get('DEFAULT', 'buildmap')) + ".kml "
                 " --max-nodes=" + (config.get('splitter', 'maxnodes')) + 
                 " --overlap=0 ")
  areas_list = (" --split-file=" + (WORK_DIR) + "areas/" + (config.get('DEFAULT', 'buildmap')) + "_areas.list ")
  map_data = ((WORK_DIR) + (BUILD_O5M))

  ExitCode = os.path.exists("areas/" + (config.get('DEFAULT', 'buildmap')) + "_areas.list")
  if ExitCode == True:
    os.chdir("tiles")
    os.system((java_opts) + (splitter_opts) + (areas_list) + (map_data))
  else:
    os.chdir("tiles")
    os.system((java_opts) + (splitter_opts) + (map_data))
    os.system("cp areas.list ../areas/" + (config.get('DEFAULT', 'buildmap')) + "_areas.list")
  datei = open((WORK_DIR) + "tiles/" + (config.get('DEFAULT', 'buildmap')) + "_split.ready", "w")
  datei.close()
  os.remove((WORK_DIR) + "tiles/" + (config.get('DEFAULT', 'buildmap')) + "_split.lck")