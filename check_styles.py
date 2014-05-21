#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser

WORK_DIR = os.environ['HOME'] + "/map_build/"

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


config = configparser.ConfigParser()


def check():
  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')
  option_mkgmap_path = (WORK_DIR) + config.get('mkgmap', 'version') + "/mkgmap.jar "

  for layer in config['map_styles']:
    if config['map_styles'][(layer)] == "yes":
      print()
      print(layer)


      if (layer == "defaultmap"):
        option_typ_file = " "
        option_style_file = (WORK_DIR) + config.get('mkgmap', 'version') + "/examples/styles/default "

      else:
        if os.path.exists((WORK_DIR) + "mystyles/" + (layer) + "_typ.txt") == True:
          if config.get('runtime', 'verbose') == "yes":
            print()
            printinfo((layer) + " build with " + (layer) + "typ.txt")
          option_typ_file = (WORK_DIR) + "mystyles/" + (layer) + "_typ.txt"

        elif os.path.exists((WORK_DIR) + "mystyles/pygmap3_typ.txt") == True:
          if config.get('runtime', 'verbose') == "yes":
            print()
            printinfo((layer) + " build with pygmap3_typ.txt")
          option_typ_file = (WORK_DIR) + "mystyles/pygmap3_typ.txt"

        else:
          print()
          printwarning((layer) + " build without a typ_file")
          option_typ_file = " "

        option_style_file = (WORK_DIR) + "mystyles/" + (layer) + "_style "


      print()
      print("typ_file   = " + option_typ_file)
      print("style_file = " + option_style_file)
      print()
      os.system("java -jar " + (option_mkgmap_path) + " --style-file=" + (option_style_file) + " --check-styles " + (option_typ_file))
      print()
