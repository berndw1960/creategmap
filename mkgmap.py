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

def typ_txt_test():
  global option_typ_file
  global option_style_file
  if (layer == "defaultmap"):

    option_typ_file = " "
    option_style_file = (WORK_DIR) + config.get('runtime', 'mkgmap') + "/examples/styles/default "

  else:
    if os.path.exists((WORK_DIR) + "styles/" + (layer) + "_typ.typ") == True:
      printinfo((layer) + " build with " + (layer) + "_typ.typ")
      option_typ_file = " " + (WORK_DIR) + "styles/" + (layer) + "_typ.typ"

    elif os.path.exists((WORK_DIR) + "styles/" + (layer) + "_typ.txt") == True:
      printinfo((layer) + " build with " + (layer) + "_typ.txt")

    elif os.path.exists((WORK_DIR) + "styles/styles_typ.typ") == True:
      if os.path.exists((WORK_DIR) + "styles/styles_typ.txt") == True:
        m1 = os.path.getmtime((WORK_DIR) + "styles/styles_typ.typ")
        m2 = os.path.getmtime((WORK_DIR) + "styles/styles_typ.txt")
        if m1 < m2:
          print()
          printwarning("styles_typ.typ is older then styles_typ.txt, renew it")
          os.remove((WORK_DIR) + "styles/styles_typ.typ")

      if os.path.exists((WORK_DIR) + "styles/styles_typ.typ") == True:
        option_typ_file = " " + (WORK_DIR) + "styles/styles_typ.typ"
      else:
        option_typ_file = " " + (WORK_DIR) + "styles/styles_typ.txt"
        print()
        printwarning((layer) + " build with styles_typ.txt")

    elif os.path.exists((WORK_DIR) + "styles/styles_typ.txt") == True:
      option_typ_file = " " + (WORK_DIR) + "styles/styles_typ.txt"

    else:
      print()
      printwarning((layer) + " build without a typ_file")
      option_typ_file = " "

    option_style_file = " --style-file=" + (WORK_DIR) + "styles/" + (layer) + "_style "

"""
style check

"""

def check():
  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')
  option_mkgmap_path = (WORK_DIR) + config.get('runtime', 'mkgmap') + "/mkgmap.jar "

  global layer
  for layer in config['map_styles']:
    if config['map_styles'][(layer)] == "yes":
      print()
      print()
      printinfo("checking needed files to build " + (layer))
      typ_txt_test()
      print()
      printinfo("typ_file   = " + option_typ_file)
      print()
      printinfo("style_file = " + option_style_file)
      print()
      os.system("java -jar " + (option_mkgmap_path) + " --style-file=" + (option_style_file) + " --check-styles " + (option_typ_file))
  print()

  for i in ['styles_typ.typ', 'styles/xstyles_typ.typ', 'splitter.log', 'osmmap.tdb']:
    if os.path.exists(i) == True:
      os.remove(i)

"""
map rendering

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
      Test for (layer)-dir and remove old data from there
      """

      if os.path.exists(layer) == False:
        os.mkdir(layer)
      else:
        path = (layer)
        for file in os.listdir(path):
          if os.path.isfile(os.path.join(path, file)):
            try:
              os.remove(os.path.join(path, file))
            except:
              print()
              print('Could not delete', file, 'in', path)

      os.chdir(layer)
      print()
      printinfo("building " + (layer))

      """
      mkgmap-options
      """

      option_mkgmap_path = (WORK_DIR) + config.get('runtime', 'mkgmap') + "/mkgmap.jar "

      if (layer) == "defaultmap":
        option_mkgmap_options = " --route --gmapsupp --read-config=" + (WORK_DIR) + config.get('runtime', 'mkgmap') + "/examples/styles/default/options "
      else:
        option_mkgmap_options = " --read-config=" + (WORK_DIR) + "styles/" + (layer) + "_style/options "

      if config.get('runtime', 'logging') == "yes":
        if config.get('runtime', 'verbose') == "yes":
          print()
          printinfo("logging enabled")
        option_mkgmap_logging = " -Dlog.config=" + (WORK_DIR) + "mkgmap_log.props "
      else:
        option_mkgmap_logging = " "

      option_bounds = " --location-autofill=bounds,is_in,nearest "
      option_sea = " --generate-sea=extend-sea-sectors,close-gaps=6000,floodblocker,land-tag=natural=background "

      if config.get('navmap', 'pre_comp') == "yes":
        if config.get('navmap', 'use_bounds') == "yes":
          if config.get('runtime', 'verbose') == "yes":
            print()
            printinfo ("use precompiled bounds")
          option_bounds = " --bounds=" + (WORK_DIR) + config.get('navmap', 'bounds_rev') + ".zip "

        if config.get('navmap', 'use_sea') == "yes":
          if config.get('runtime', 'verbose') == "yes":
            print()
            printinfo ("use precompiled sea_tiles")
            print()
          option_sea = " --precomp-sea=" + (WORK_DIR) + config.get('navmap', 'sea_rev') + ".zip  --generate-sea "


      typ_txt_test()

      """
      map rendering
      """

      os.system("java -ea " +
            config.get('runtime', 'ramsize') +
            (option_mkgmap_logging) +
            " -jar " + (option_mkgmap_path) +
            (option_mkgmap_options) +
            (option_bounds) +
            (option_sea) +
            (option_style_file) +
            " --name-tag-list=name:de,name,name:en,int_name " +
            " --mapname=" + config.get('mapid', (buildmap)) + config.get((layer), 'mapid_ext') +
            " --family-id=" + config.get((layer), 'family-id') +
            " --product-id=" + config.get((layer), 'product-id') +
            " --description=" + (buildmap) + "_" + (buildday) + "_" + (layer) +
            " --family-name=" + config.get((layer), 'family-name') +
            " --draw-priority=" + config.get((layer), 'draw-priority') + " " +
            (WORK_DIR) + "tiles/*.o5m " +
            (option_typ_file))

      os.chdir(WORK_DIR)

      """
      move gmapsupp.img to (unzip_dir) as (buildmap)_(layer)_gmapsupp.img
      """

      unzip_dir = "gps_ready/unzipped/" + (buildmap)

      bl = (buildmap) + "_" + (layer)
      img = (unzip_dir) + "/" + (bl) + "_gmapsupp.img"

      if os.path.exists(unzip_dir) == False:
        os.makedirs(unzip_dir)

      if os.path.exists(img) == True:
        os.remove(img)

      shutil.move((layer) +"/gmapsupp.img", (img))
