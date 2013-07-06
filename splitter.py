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
  buildday = config.get('time_stamp', (buildmap))

  datei = open((WORK_DIR) + "tiles/" + (buildmap) + "_split.lck", "w")
  datei.close()

  java_opts = ("java -ea " + (config.get('ramsize', 'ramsize')) +
                  " -jar " + (config.get('runtime', 'splitter_path')))

  logging = config.get('splitter', 'logging')
  if logging == "yes":

    log_dir = ((WORK_DIR) + "log/splitter/" + (buildday) + "/" + (buildmap))

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

    log_opts = (" > " + (log_dir) + "/splitter.log ")

  else:
    log_opts = (" ")

  """
  splitter-options
  """

  splitter_opts = (" --geonames-file=" + (WORK_DIR) + "cities15000.zip " +
                   " --mapid=" + config.get('runtime', 'option_mapid') + "0001 " +
                   " --output=o5m " +
                   " --keep-complete " +
                   " --write-kml=" + (buildmap) + ".kml "
                   " --max-nodes=" + (config.get('splitter', 'maxnodes')) +
                   " --overlap=0 ")

  areas_list = (" --split-file=" + (WORK_DIR) + "areas/" + (buildmap) + "_areas.list ")

  BUILD_O5M = ((WORK_DIR) + "o5m/" + (buildmap) + ".o5m")

  ExitCode = os.path.exists((WORK_DIR) + "areas/" + (buildmap) + "_areas.list")
  if ExitCode == True:
    os.chdir((WORK_DIR) + "tiles")
    os.system((java_opts) + (log_opts) + (splitter_opts) + (areas_list) + (BUILD_O5M))
  else:
    os.chdir((WORK_DIR) + "tiles")
    os.system((java_opts) + (log_opts) + (splitter_opts) + (BUILD_O5M))
    os.system("cp areas.list " + (WORK_DIR) + "/areas/" + (buildmap) + "_areas.list")

  ExitCode = os.path.exists((WORK_DIR) + "tiles/template.args")
  if ExitCode == True:
    datei = open((WORK_DIR) + "tiles/" + (buildmap) + "_split.ready", "w")
    datei.close()
  else:
    printerror("Splitter-Error!")
    quit()
  os.remove((WORK_DIR) + "tiles/" + (buildmap) + "_split.lck")

