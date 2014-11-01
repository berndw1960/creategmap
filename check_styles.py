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
  option_mkgmap_path = (WORK_DIR) + config.get('runtime', 'mkgmap') + "/mkgmap.jar "

  for layer in config['map_styles']:
    if config['map_styles'][(layer)] == "yes":
      print()
      printinfo(layer)


      if (layer == "defaultmap"):
        option_typ_file = " "
        option_style_file = (WORK_DIR) + config.get('runtime', 'mkgmap') + "/examples/styles/default "

      else:
        if os.path.exists((WORK_DIR) + "styles/" + (layer) + "_typ.txt") == True:
          if config.get('runtime', 'verbose') == "yes":
            print()
            printinfo((layer) + " build with " + (layer) + "typ.txt")
          option_typ_file = (WORK_DIR) + "styles/" + (layer) + "_typ.txt"

        elif os.path.exists((WORK_DIR) + "styles/styles_typ.txt") == True:
          if config.get('runtime', 'verbose') == "yes":
            print()
            printinfo((layer) + " build with styles_typ.txt")
          option_typ_file = (WORK_DIR) + "styles/styles_typ.txt"

        else:
          print()
          printwarning((layer) + " build without a typ_file")
          option_typ_file = " "

        option_style_file = (WORK_DIR) + "styles/" + (layer) + "_style "


      print()
      printinfo("typ_file   = " + option_typ_file)
      print()
      printinfo("style_file = " + option_style_file)
      print()
      os.system("java -jar " + (option_mkgmap_path) + " --style-file=" + (option_style_file) + " --check-styles " + (option_typ_file))


  for i in ['styles_typ.typ', 'housenumber_typ.typ', 'fixme_typ.typ', 'splitter.log', 'osmmap.tdb']:
    ExitCode = os.path.exists(i)
    if ExitCode == True:
      os.remove(i)

  print()
