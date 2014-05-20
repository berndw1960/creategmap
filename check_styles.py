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
  mkgmap_path = (WORK_DIR) + config.get('mkgmap', 'version') + "/mkgmap.jar "

  for layer in config['map_styles']:
    if config['map_styles'][(layer)] == "yes":
      print()
      print(layer)
      if layer != "defaultmap":
        if os.path.exists((WORK_DIR) + "mystyles/" + (layer) + "_typ.txt") == True:
          typ_file = " " + (WORK_DIR) + "mystyles/" + (layer) + "_typ.txt"
        elif os.path.exists((WORK_DIR) + "mystyles/pygmap3_typ.txt") == True:
          typ_file = " " + (WORK_DIR) + "mystyles/pygmap3_typ.txt"
        else:
          typ_file = " "
        style_file = " --style-file=" + (WORK_DIR) + "mystyles/" + (layer) + "_style "
        print()
        print("typ_file = " + typ_file)
        print("style_file = " + style_file)
        print()
        os.system("java -jar " + (mkgmap_path) + (style_file) + " --check-styles " + (typ_file))
        print()
