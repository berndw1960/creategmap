#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import shutil

WORK_DIR = os.environ['HOME'] + "/map_build/"

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)

config = configparser.ConfigParser()

"""
split raw-data

"""

def split():

  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')
  buildday = config.get('time_stamp', (buildmap))
  splitter_path = (WORK_DIR) + config.get('runtime', 'splitter') + "/splitter.jar "

  java_opts = ("java -ea " + config.get('runtime', 'ramsize') +
                  " -jar " + (splitter_path))


  log_opts = (" > splitter.log ")

  """
  splitter-options
  """

  pre_comp = " "
  if config.get('navmap', 'pre_comp') == "yes":
    if config.get('navmap', 'use_sea') == "yes":
      pre_comp = " --precomp-sea=" + (WORK_DIR) + "sea_"+ config.get('navmap', 'sea') + ".zip "

  if config.get('runtime','use_cities15000') == "yes":
    geonames = " --geonames-file=" + (WORK_DIR) + "cities15000.zip "
  else:
    geonames = " "

  splitter_opts = ((geonames) +
                   " --mapid=" + config.get('mapid', (buildmap)) + "0001 " +
                   " --output=o5m " +
                   (pre_comp) +
                   " --write-kml=" + (buildmap) + ".kml " +
                   " --keep-complete " +
                   " --overlap=0 ")

  ## split with
  areas_list = " --split-file=" + (WORK_DIR) + "areas/" + (buildmap) + "_areas.list "
  ## or
  max_nodes = (" --max-nodes=" + config.get('runtime', 'maxnodes') + " ")

  BUILD_O5M = (WORK_DIR) + "o5m/" + (buildmap) + ".o5m"

  use_areas = config.get('runtime', 'use_areas')
  if use_areas == "yes":
    if os.path.exists("areas/" + (buildmap) + "_areas.list") == True:
      os.chdir("tiles")
      if config.get('runtime', 'verbose') == "yes":
        print()
        printinfo("splitting the mapdata with areas.list...")
      if config.get('runtime', 'verbose') == "yes":
        printinfo((java_opts) + (log_opts) + (splitter_opts) + (areas_list) + (BUILD_O5M))
      os.system((java_opts) + (log_opts) + (splitter_opts) + (areas_list) + (BUILD_O5M))
    else:
      os.chdir("tiles")
      if config.get('runtime', 'verbose') == "yes":
        print()
        printinfo("create areas.list and splitting the mapdata...")
        printinfo((java_opts) + (log_opts) + (splitter_opts) + (max_nodes) + (BUILD_O5M))
      os.system((java_opts) + (log_opts) + (splitter_opts) + (max_nodes) + (BUILD_O5M))
      shutil.copy2("areas.list", (WORK_DIR) + "areas/" + (buildmap) + "_areas.list")
  else:
    os.chdir("tiles")
    if config.get('runtime', 'verbose') == "yes":
      print()
      printinfo("'--areas_list' isn't enabled, splitting the mapdata without it...")
    os.system((java_opts) + (log_opts) + (splitter_opts) + (max_nodes) + (BUILD_O5M))

  if config.get('runtime', 'logging') == "yes":
    log_dir = ((WORK_DIR) + "log/splitter/" + (buildmap) + "/" + (buildday))

    if os.path.exists(log_dir) == True:
      path = (log_dir)
      for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
          try:
            os.remove(os.path.join(path, file))
          except:
            print('Could not delete', file, 'in', path)

    else:
      os.makedirs(log_dir)

    for i in ['densities-out.txt', 'template.args', 'areas.poly', 'splitter.log', 'areas.list']:
      if os.path.exists(i) == True:
        shutil.copy2((i), (log_dir))

  os.chdir(WORK_DIR)

  if os.path.exists("tiles/template.args") == True:
    datei = open("tiles/" + (buildmap) + "_split.ready", "w")
    datei.close()
  else:
    if os.path.exists("areas/" + (buildmap) + "_areas.list") == True:
      os.remove("areas/" + (buildmap) + "_areas.list")
      print()
      printwarning((buildmap) + "_areas.list removed, next build creates a new one")
    print()
    printerror("Splitter-Error!")
    print("Please restart the buildprocess for " + (buildmap))
    print()
    printerror("If this error comes again after the next start, please remove")
    print("  " + (WORK_DIR) + "o5m/"  + (buildmap) + ".o5m")
    print("Maybe this file is damaged")
    print()
    quit()
