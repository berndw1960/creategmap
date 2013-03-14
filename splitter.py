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

"""
split raw-data

"""

def split():

  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')

  datei = open((WORK_DIR) + "tiles/" + (buildmap) + "_split.lck", "w")
  datei.close()

  java_opts = ("java -ea " + (config.get('ramsize', 'ramsize')) +
                  " -jar " + (config.get('runtime', 'splitter_path')))

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

