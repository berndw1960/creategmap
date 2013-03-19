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
map-rendering

"""

def render():
  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')
  buildday = config.get('mapdata', 'buildday')

  global layer
  for layer in config['map_styles']:
    build = (config['map_styles'][(layer)])
    if build == "yes":
      os.chdir(WORK_DIR)

      """
      create the layers
      add your own styles in mystyles

      """

      ExitCode = os.path.exists((WORK_DIR) + "mystyles/" + (layer) + "_style")
      global mapstyle
      if ExitCode == True:
        mapstyle = "mystyles"
      else:
        ExitCode = os.path.exists((WORK_DIR) + "aiostyles")
        if ExitCode == False:
          ExitCode = os.path.exists((WORK_DIR) + "aiostyles.7z")
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
      Test for (layer)-dir and remove old data from there
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

      os.chdir(layer)
      printinfo("entered " + os.getcwd())
      printinfo("Now building " + (layer) + "-layer with " + (mapstyle))


      """
      mkgmap-options
      """

      logging = config.get('mkgmap', 'logging')
      if logging == "yes":
        printinfo("logging enabled")
        option_mkgmap_logging = " -Dlog.config=" + (WORK_DIR) + "log.conf "
      else:
        printwarning("logging disabled")
        option_mkgmap_logging = " "

      os.system("java -ea " + (config.get('ramsize', 'ramsize')) +
            (option_mkgmap_logging) +
            " -jar " + (config.get('runtime', 'mkgmap_path')) +
            " -c "  + (WORK_DIR) + (config.get((layer), 'conf')) +
            " --style-file=" + (WORK_DIR) + (mapstyle) + "/" + (layer) + "_style " +
            " --bounds=" + (config.get('runtime', 'bounds_rev_path')) +
            " --precomp-sea=" + (config.get('runtime', 'sea_rev_path')) +
            " --generate-sea " +
            " --mapname=" + (config.get('mapid', 'mapid')) + (config.get((layer), 'mapid_ext')) +
            " --family-id=" + (config.get((layer), 'family-id')) +
            " --product-id=" + (config.get((layer), 'product-id')) +
            " --description=" + (config.get('runtime', 'description')) +
            " --family-name=" + (config.get((layer), 'family-name')) +
            " --draw-priority=" + (config.get((layer), 'draw-priority')) + " " +
            (WORK_DIR) + "tiles/*.o5m " +
            (WORK_DIR) + (mapstyle) + "/" + (layer) + "_typ.txt")

      """
      move the ready gmapsupp.img to destination (unzip_dir) and
      rename it to (buildmap)_gmapsupp.img
      """

      unzip_dir = ((WORK_DIR) + "gps_ready/unzipped/" + (buildmap) + "/" + (buildday) + "/")

      os.system("cp gmapsupp.img " + (unzip_dir) + (buildmap) + "_" + (layer) + "_gmapsupp.img")


      """
      save the mkgmap-log for errors
      """

      logging = config.get('mkgmap', 'logging')
      if logging == "yes":
        log_dir = ((WORK_DIR) + "log/" + (buildmap) + "/" + (buildday) + "/" + (layer) + "/")


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
