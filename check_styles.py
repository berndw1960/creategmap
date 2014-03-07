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
    print()
    print()
    print(layer)
    if config['map_styles'][(layer)] == "yes":
      if layer != "defaultmap":
        typ_file = " " + (WORK_DIR) + "mystyles/" + (layer) + "_typ.txt"
        style_file = " --style-file=" + (WORK_DIR) + "mystyles/" + (layer) + "_style "
        print()
        print()
        print(typ_file)
        print(style_file)
        print()
        print()
        
        os.system("java -jar " + (mkgmap_path) + (style_file) + " --check-styles " + (typ_file))
       
"""
     if config.get('runtime', 'verbose') == "yes":
          printinfo("list_styles enabled")
        option_list_styles = " --list-styles "
      else:
        if config.get('runtime', 'verbose') == "yes":
          printwarning("list_styles disabled")
        option_list_styles = " "


"""