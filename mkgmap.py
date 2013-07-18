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
map-rendering

"""

def render():
  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')
  buildday = config.get('time_stamp', (buildmap))

  global layer
  for layer in config['map_styles']:
    build = (config['map_styles'][(layer)])
    if build == "yes":
      os.chdir(WORK_DIR)

      """
      create the layers
      add your own styles in mystyles

      """

      ExitCode = os.path.exists("mystyles/" + (layer) + "_style")
      global mapstyle
      if ExitCode == True:
        mapstyle = "mystyles"
      else:
        printerror("no " + (layer) + "_style found!")
        quit()

      """
        Use of AIO-Styles disabled, while unusable and outdated

        ExitCode = os.path.exists("aiostyles")
        if ExitCode == False:
          ExitCode = os.path.exists("aiostyles.7z")
          if ExitCode == False:
            os.system("wget -N http://dev.openstreetmap.de/aio/aiostyles.7z")

          os.system("7z x aiostyles.7z -oaiostyles")

        mapstyle = "aiostyles"
      """
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

      zip_dir = (WORK_DIR) + "gps_ready/zipped/" + (buildmap) + "/"
      unzip_dir = (WORK_DIR) + "gps_ready/unzipped/" + (buildmap) + "/"


      for dir in [(zip_dir), (unzip_dir)]:
        ExitCode = os.path.exists(dir)
        if ExitCode == False:
          os.makedirs(dir)

      """
      Test for (layer)-dir and remove old data from there
      """

      ExitCode = os.path.exists(layer)
      if ExitCode == False:
        os.mkdir(layer)
      else:
        path = (layer)
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


      if config.get('mkgmap', 'logging') == "yes":
        printinfo("logging enabled")
        option_mkgmap_logging = " -Dlog.config=" + (WORK_DIR) + "log.conf "
      else:
        printwarning("logging disabled")
        option_mkgmap_logging = " "

      if config.get('navmap', 'bounds') == "yes":
        printinfo ("use precompiled bounds")
        option_bounds = " --bounds=" + (WORK_DIR) + "bounds.zip "
        option_sea = " --precomp-sea=" + (WORK_DIR) + "sea.zip  --generate-sea "
      else:
        option_bounds = " --location-autofill=is_in, nearest "
        option_sea = " --generate-sea=extend-sea-sectors,close-gaps=6000,floodblocker,land-tag=natural=background "

      if config.get('mkgmap', 'check_styles') == "yes":
        printinfo("check_styles enabled")
        option_check_styles = " --check-styles "
      else:
        printwarning("check_styles disabled")
        option_check_styles = " "

      if config.get('mkgmap', 'list_styles') == "yes":
        printinfo("list_styles enabled")
        option_list_styles = " --list-styles "
      else:
        printwarning("list_styles disabled")
        option_list_styles = " "


      """
      map rendering

      """
      mkgmap_path = (WORK_DIR) + config.get('mkgmap', 'version') + "/mkgmap.jar "

      os.system("java -ea " + config.get('ramsize', 'ramsize') +
            (option_mkgmap_logging) +
            " -jar " + (mkgmap_path) +
            (option_mkgmap_options) +
            (option_bounds) +
            (option_sea) +
            " --style-file=" + (WORK_DIR) + (mapstyle) + "/" + (layer) + "_style " +
            (option_check_styles) +
            (option_list_styles) +
            " --name-tag-list=name:de,name,name:en,int_name "
            " --mapname=" + config.get('mapid', (buildmap)) + config.get((layer), 'mapid_ext') +
            " --family-id=" + config.get((layer), 'family-id') +
            " --product-id=" + config.get((layer), 'product-id') +
            " --description=" + (buildmap) + "_" + (buildday) +
            " --family-name=" + config.get((layer), 'family-name') +
            " --draw-priority=" + config.get((layer), 'draw-priority') + " " +
            (WORK_DIR) + "tiles/*.o5m " +
            (WORK_DIR) + (mapstyle) + "/" + (layer) + "_typ.txt")


      """
      move the ready gmapsupp.img to destination (unzip_dir) and
      rename it to (buildmap)_(layer)_gmapsupp.img
      """

      bl = (buildmap) + "_" + (layer)
      move_img = (bl) + "_gmapsupp.img"
      move_zip = (bl) + "_gmapsupp.img.zip"
      move_7z = (bl) + "_gmapsupp.img.7z"

      ExitCode = os.path.exists(move_img)
      if ExitCode == True:
        os.remove(move_img)
      shutil.move('gmapsupp.img', (move_img))

      """
      zipp the images and mv them to separate dirs

      """

      if config.get('store_as', 'zip_img') == "yes":
        os.chdir(unzip_dir)
        os.system(("zip ") + (move_zip) + " " + (move_img))
        ExitCode = os.path.exists((zip_dir) + (move_zip))
        if ExitCode == True:
          os.remove((zip_dir) + (move_zip))
        shutil.move((move_zip), (zip_dir))

      if config.get('store_as', '7z_img') == "yes":
        os.chdir(unzip_dir)
        os.system(("7z a  ") + (move_7z) + " " + (move_img))
        ExitCode = os.path.exists((zip_dir) + (move_7z))
        if ExitCode == True:
          os.remove((zip_dir) + (move_7z))
        shutil.move((move_7z), (zip_dir))

      """
      save the mkgmap-log for errors
      """
      os.chdir(WORK_DIR)

      if config.get('mkgmap', 'logging') == "yes":
        log_dir = ("log/mkgmap/" + (buildday) + "/" + (buildmap) + "/" + (layer))

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

      ExitCode = os.path.exists((layer) + "/mkgmap.log.0")
      if ExitCode == True:
        shutil.move((layer) + "/mkgmap.log.*", (log_dir))






