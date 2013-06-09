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
  os.chdir(WORK_DIR)
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
      create dirs to store the images

      """

      os.chdir(WORK_DIR)

      zip_dir = ((WORK_DIR) + "gps_ready/zipped/" + (buildmap) + "/" + (buildday) + "/")
      unzip_dir = ((WORK_DIR) + "gps_ready/unzipped/" + (buildmap) + "/" + (buildday) + "/")

      cl_dir = ((WORK_DIR) + "contourlines/" + (buildmap) + "/")
      cltemp_dir = ((WORK_DIR) + "contourlines/temp/")

      for dir in [(zip_dir), (unzip_dir), (cltemp_dir), (cl_dir)]:
        ExitCode = os.path.exists(dir)
        if ExitCode == False:
          os.makedirs(dir)

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
      option_mkgmap_options = " --read-config=" + (WORK_DIR) + (mapstyle) + "/" + (layer) + "_style/options "


      logging = config.get('mkgmap', 'logging')
      if logging == "yes":
        printinfo("logging enabled")
        option_mkgmap_logging = " -Dlog.config=" + (WORK_DIR) + "log.conf "
      else:
        printwarning("logging disabled")
        option_mkgmap_logging = " "

      bounds = config.get('navmap', 'bounds')
      if bounds == "yes":
        printinfo ("use precompiled bounds")
        option_bounds = " --bounds=" + (WORK_DIR) + "bounds.zip "
        option_sea = " --precomp-sea=" + (WORK_DIR) + "sea.zip  --generate-sea "
      else:
        option_bounds = " --location-autofill=is_in, nearest "
        option_sea = " --generate-sea=extend-sea-sectors,close-gaps=6000,floodblocker,land-tag=natural=background "

      check_styles = config.get('mkgmap', 'check_styles')
      if check_styles == "yes":
        printinfo("check_styles enabled")
        option_1 = " --check-styles "
        option_check_styles = str(option_1)
      else:
        printwarning("check_styles disabled")
        option_check_styles = " "

      list_styles = config.get('mkgmap', 'list_styles')
      if list_styles == "yes":
        printinfo("list_styles enabled")
        option_2 = " --list-styles "
        option_list_styles = str(option_2)
      else:
        printwarning("list_styles disabled")
        option_list_styles = " "


      """
      map rendering

      """

      os.system("java -ea " + (config.get('ramsize', 'ramsize')) +
            (option_mkgmap_logging) +
            " -jar " + (config.get('runtime', 'mkgmap_path')) +
            (option_mkgmap_options) +
            (option_bounds) +
            (option_sea) +
            " --style-file=" + (WORK_DIR) + (mapstyle) + "/" + (layer) + "_style " +
            (option_check_styles) +
            (option_list_styles) +
            " --name-tag-list=name:de,name,name:en,int_name "
            " --mapname=" + (config.get('runtime', 'option_mapid')) + (config.get((layer), 'mapid_ext')) +
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

      ExitCode = os.path.exists((unzip_dir) + (buildmap) + "_" + (layer) + "_gmapsupp.img")
      if ExitCode == True:
        os.remove((unzip_dir) + (buildmap) + "_" + (layer) + "_gmapsupp.img")
      os.system("cp gmapsupp.img " + (unzip_dir) + (buildmap) + "_" + (layer) + "_gmapsupp.img")

      """
      zipp the images and mv them to separate dirs

      """

      zip_img = (config.get('store_as', 'zip_img'))
      if zip_img == "yes":
        os.chdir(unzip_dir)
        os.system(("zip ") + (buildmap) + "_" + (layer) + "_gmapsupp.img.zip " + (buildmap) + "_" + (layer) + "_gmapsupp.img")
        ExitCode = os.path.exists((zip_dir) + (buildmap) + "_" + (layer) + "_gmapsupp.img.zip")
        if ExitCode == True:
          os.remove((zip_dir) + (buildmap) + "_" + (layer) + "_gmapsupp.img.zip")
        os.system(("mv ") + (buildmap) + "_" + (layer) + "_gmapsupp.img.zip " + (zip_dir))

      """
      save the mkgmap-log for errors
      """
      os.chdir(WORK_DIR)
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

      """
      copy *kml to zipp-dirs

      """

      os.chdir(WORK_DIR)

      ExitCode = os.path.exists("tiles/" + (buildmap) + ".kml")
      if ExitCode == True:
        os.system("mv tiles/" + (buildmap) + ".kml " + (zip_dir))





