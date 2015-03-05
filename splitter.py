#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import shutil
import time

WORK_DIR = os.environ['HOME'] + "/map_build/"

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)
config = configparser.ConfigParser()

"""
split raw-data

"""

def split():

  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')
  buildmap = config['runtime']['buildmap']
  buildday = config['time_stamp'][buildmap]
  splitter_path = WORK_DIR + config['runtime']['splitter'] + "/splitter.jar "

  java_opts = ("java -ea " + config['runtime']['ramsize'] +
                  " -jar " + splitter_path)


  log_opts = " > splitter.log "

  """
  splitter-options
  """

  BUILD_O5M = " " + WORK_DIR + "o5m/" + buildmap + ".o5m"

  sea_zip = WORK_DIR + "sea_"+ config['navmap']['sea'] + ".zip"
  if os.path.exists(sea_zip):
    option_sea = " --precomp-sea=" + sea_zip
  else:
    option_sea = " "

  splitter_opts = (" --description=" + buildmap + "_" + buildday +
                   " --mapid=" + config['mapid'][buildmap] + "0001 " +
                   " --output=o5m " +
                   option_sea +
                   " --write-kml=" + buildmap + ".kml " +
                   " --keep-complete " +
                   " --overlap=0 ")

  ## split with
  areas_list = WORK_DIR + "areas/" + buildmap + "_areas.list"
  areas = " --split-file=" + areas_list
  ## or
  max_nodes = (" --max-nodes=" + config['runtime']['maxnodes'] + " ")

  split_with_areas_list = java_opts + log_opts + splitter_opts + areas + BUILD_O5M
  split_without_areas_list = java_opts + log_opts + splitter_opts + max_nodes + BUILD_O5M


  if os.path.exists(areas_list) == True:
    command_line = split_with_areas_list
  else:
    command_line = split_without_areas_list

  if config['runtime']['verbose'] == "yes":
    print()
    printinfo(command_line)
    print()

  os.chdir("tiles")
  os.system(command_line)

  if config['runtime']['logging'] == "yes":
    log_dir = (WORK_DIR + "log/splitter/" + buildmap + "/" + buildday)

    if os.path.exists(log_dir) == True:
      path = log_dir
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
        shutil.copy2(i, log_dir)


  if os.path.exists(areas_list) == False:
    shutil.copy2("areas.list", areas_list)
  datei = open(buildmap + "_split.ready", "w")
  datei.close()
