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

    if config['map_styles'][(layer)] == "yes":
      os.chdir(WORK_DIR)

      """
      create the layers
      add your own styles in mystyles

      """
      if layer !=  'defaultmap':
        ExitCode = os.path.exists("mystyles/" + (layer) + "_style")
        if ExitCode == False:
          printerror("no " + (layer) + "_style found!")
          quit()

        """
        if there is only a TYP-File

        """
        ExitCode = os.path.exists("mystyles/" + (layer) + "_typ.txt")
        if ExitCode == False:
          ExitCode = os.path.exists("mystyles/" + (layer) + "_typ")
          if ExitCode == True:
            printerror(" Please convert " +
              "mystyles/" + (layer) + ".TYP to " + (layer) + "_typ.txt!")
            quit()


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
      printinfo("Now building " + (layer))

      """
      mkgmap-options
      """
      option_mkgmap_options = " --read-config=" + (WORK_DIR) + "mystyles/" + (layer) + "_style/options "


      if config.get('mkgmap', 'logging') == "yes":
        if config.get('verbose', 'verbose') == "yes":
          printinfo("logging enabled")
        option_mkgmap_logging = " -Dlog.config=" + (WORK_DIR) + "log.conf "
      else:
        if config.get('verbose', 'verbose') == "yes":
          printwarning("logging disabled")
        option_mkgmap_logging = " "

      if config.get('navmap', 'pre_comp') == "yes":
        if config.get('navmap', 'use_bounds') == "yes":
          if config.get('verbose', 'verbose') == "yes":
            printinfo ("use precompiled bounds")
          option_bounds = " --bounds=" + (WORK_DIR) + "bounds_" + config.get('navmap', 'bounds_rev') + ".zip "
        else:
          option_bounds = " --location-autofill=bounds,is_in,nearest "
          
        if config.get('navmap', 'use_sea') == "yes":
          if config.get('verbose', 'verbose') == "yes":
            printinfo ("use precompiled sea_tiles")
          option_sea = " --precomp-sea=" + (WORK_DIR) + "sea_" + config.get('navmap', 'sea_rev') + ".zip  --generate-sea "
        else:
          option_sea = " --generate-sea=extend-sea-sectors,close-gaps=6000,floodblocker,land-tag=natural=background "

      else:
        option_bounds = " --location-autofill=bounds,is_in,nearest "
        option_sea = " --generate-sea=extend-sea-sectors,close-gaps=6000,floodblocker,land-tag=natural=background "
        
      if layer == "defaultmap":
        printwarning("defaultmap has no typ_file")
        typ_file = " "
        style_file = " "
      else:
        if config.get('verbose', 'verbose') == "yes":
          printinfo((layer) + " build with typ_file")
        typ_file = " " + (WORK_DIR) + "mystyles/" + (layer) + "_typ.txt"
        style_file = " --style-file=" + (WORK_DIR) + "mystyles/" + (layer) + "_style "

      if config.get('mkgmap', 'check_styles') == "yes":
        if config.get('verbose', 'verbose') == "yes":
          printinfo("check_styles enabled")
        option_check_styles = " --check-styles "
      else:
        if config.get('verbose', 'verbose') == "yes":
          printwarning("check_styles disabled")
        option_check_styles = " "

      if config.get('mkgmap', 'list_styles') == "yes":
        if config.get('verbose', 'verbose') == "yes":
          printinfo("list_styles enabled")
        option_list_styles = " --list-styles "
      else:
        if config.get('verbose', 'verbose') == "yes":
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
            (style_file) +
            (option_check_styles) +
            (option_list_styles) +
            " --name-tag-list=name:de,name,name:en,int_name " +
            " --mapname=" + config.get('mapid', (buildmap)) + config.get((layer), 'mapid_ext') +
            " --family-id=" + config.get((layer), 'family-id') +
            " --product-id=" + config.get((layer), 'product-id') +
            " --description=" + (buildmap) + "_" + (buildday) + "_" + config.get('mkgmap', 'version') +
            " --family-name=" + config.get((layer), 'family-name') +
            " --draw-priority=" + config.get((layer), 'draw-priority') + " " +
            (WORK_DIR) + "tiles/*.o5m " +
            (typ_file))


      """
      move gmapsupp.img to (unzip_dir) as (buildmap)_(layer)_gmapsupp.img
      """

      os.chdir(WORK_DIR)

      unzip_dir = "gps_ready/unzipped/" + (buildmap)

      bl = (buildmap) + "_" + (layer)
      img = (unzip_dir) + "/" + (bl) + "_gmapsupp.img"

      ExitCode = os.path.exists(unzip_dir)
      if ExitCode == False:
        os.makedirs(unzip_dir)

      ExitCode = os.path.exists(img)
      if ExitCode == True:
        os.remove(img)

      shutil.move((layer) +"/gmapsupp.img", (img))




