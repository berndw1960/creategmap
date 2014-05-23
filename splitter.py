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
  splitter_path = (WORK_DIR) + config.get('splitter', 'version') + "/splitter.jar "

  java_opts = ("java -ea " + config.get('ramsize', 'ramsize') +
                  " -jar " + (splitter_path))

  logging = config.get('splitter', 'logging')
  log_dir = ((WORK_DIR) + "log/splitter/" + (buildmap) + "/" + (buildday))

  if logging == "yes":

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
    log_opts = (" > /dev/null ")

  """
  splitter-options
  """

  if config.get('navmap', 'pre_comp') == "yes":
    if config.get('navmap', 'use_sea') == "yes":
      pre_comp = " --precomp-sea=" + (WORK_DIR) + config.get('navmap', 'sea_rev') + ".zip "
    else:
      pre_comp = " "
  else:
    pre_comp = " "

  splitter_opts = (" --geonames-file=" + (WORK_DIR) + "cities15000.zip " +
                   " --mapid=" + config.get('mapid', (buildmap)) + "0001 " +
                   " --output=o5m " +
                   (pre_comp) +
                   " --write-kml=" + (buildmap) + ".kml " +
                   " --keep-complete " +
                   " --overlap=0 ")

  ## split with
  areas_list = " --split-file=" + (WORK_DIR) + "areas/" + (buildmap) + "_areas.list "
  ## or
  max_nodes = (" --max-nodes=" + config.get('splitter', 'maxnodes') + " ")

  BUILD_O5M = (WORK_DIR) + "o5m/" + (buildmap) + ".o5m"

  use_areas = config.get('splitter', 'use_areas')
  if use_areas == "yes":
    ExitCode = os.path.exists("areas/" + (buildmap) + "_areas.list")
    if ExitCode == True:
      os.chdir("tiles")
      print()
      printinfo("splitting the mapdata with areas.list...")
      os.system((java_opts) + (log_opts) + (splitter_opts) + (areas_list) + (BUILD_O5M))
    else:
      os.chdir("tiles")
      print()
      printwarning("create areas.list and splitting the mapdata...")
      os.system((java_opts) + (log_opts) + (splitter_opts) + (max_nodes) + (BUILD_O5M))
      shutil.move("areas.list", (WORK_DIR) + "areas/" + (buildmap) + "_areas.list")
  else:
    os.chdir("tiles")
    print()
    printwarning("'--areas_list' isn't enabled, splitting the mapdata without it...")
    os.system((java_opts) + (log_opts) + (splitter_opts) + (max_nodes) + (BUILD_O5M))

  for i in ['densities-out.txt', 'template.args', 'areas.poly']:
    ExitCode = os.path.exists(i)
    if ExitCode == True:
      shutil.copy2((i), (log_dir))

  os.chdir(WORK_DIR)

  ExitCode = os.path.exists("tiles/template.args")
  if ExitCode == True:
    datei = open("tiles/" + (buildmap) + "_split.ready", "w")
    datei.close()
  elif ExitCode == False:
    ExitCode = os.path.exists("areas/" + (buildmap) + "_areas.list")
    if ExitCode == True:
      os.remove("areas/" + (buildmap) + "_areas.list")
      print()
      printwarning((buildmap) + "_areas.list removed, next build creates a new one")
    print()
    printerror("Splitter-Error!")
    printerror("Please restart the buildprocess for " + (buildmap))
    print()
    printerror("If this error comes again after the next start, please remove")
    printerror("  " + (WORK_DIR) + "o5m/"  + (buildmap) + ".o5m")
    printerror("this file is possible damaged")
    print()
    quit()
