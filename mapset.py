#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import configparser
import os
import argparse

WORK_DIR = os.environ['HOME'] + "/map_build/"


"""
set prefix for messages

"""

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


"""
argparse

"""

parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\

          This Program create mapsets for different regions for Garmin PNA

          pygmap3.py creates only 'one' mapset, as example the default map for DACH

          with mapset.py, it is possible to create mapsets from a list

          You can edit the mapset list with

            'mapset.py -a dach'        add 'dach' to the mapset list
            'mapset.py -r dach'        remove 'dach' from the mapset list
            'mapset.py -l yes'         print out the mapset list
            'mapset.py -d yes'         deletes the whole list

        '''))
parser.add_argument('-a', '--add_mapset', dest='add_mapset', default='no')
parser.add_argument('-r', '--rm_mapset', dest='rm_mapset', default='no')
parser.add_argument('-l', '--list_mapset', dest='list_mapset', default='no')
parser.add_argument('-d', '--del_mapset', dest='del_mapset', default='no')
args = parser.parse_args()


"""
test if a file or dir can be found at a predefined place
raise message if fails and returns 1
on success return 0
"""

ExitCode = os.path.exists(WORK_DIR)
if ExitCode == False:
  printerror("Please create" + (WORK_DIR))
  quit()

os.chdir(WORK_DIR)


"""
configparser

"""

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

config = configparser.ConfigParser()


import build_config

ExitCode = os.path.exists("pygmap3.cfg")
if ExitCode == False:
  build_config.create()

config.read('pygmap3.cfg')

if config.has_section('mapset') == False:
    config['mapset'] = {}
    write_config()

config.read('pygmap3.cfg')

"""
set, edit or delete mapset list

"""
if (args.add_mapset) != "no":
  if config.has_option('mapset', (args.add_mapset)) == False:
    ExitCode = os.path.exists("poly/" + (args.add_mapset) + ".poly")
    if ExitCode == False:
      printerror((WORK_DIR) + "poly/" + (args.add_mapset) + ".poly not found... ")
      printerror("please create or download "+ (args.add_mapset) + ".poly")
      quit()
    config.set('mapset', (args.add_mapset), 'yes')
    write_config()

  printinfo((args.add_mapset) + " added to mapset list")
  quit()

elif (args.rm_mapset) != "no":
  if config.has_section('mapset') == True:
    config.remove_option('mapset', (args.rm_mapset))
    write_config()
  printwarning((args.rm_mapset) + " removed from mapset list")
  quit()

elif (args.list_mapset) != "no":
  if config.has_section('mapset') == True:
    printinfo("mapset list includes: ")
    for key in (config['mapset']):
      print ("  " + (key) + " = " + config['mapset'][(key)])
  else:
    printwarning("mapset list not found")
  quit()

elif (args.del_mapset) != "no":
  if config.has_section('mapset') == True:
    config.remove_section('mapset')
    write_config()
  printwarning("mapset list deleted")
  quit()

for buildmap in config['mapset']:
  if (buildmap) != "default":
    if config['mapset'][(buildmap)] == "yes":
      os.system("pygmap3 -b " + (buildmap))

printinfo("")
printinfo("")
printinfo("###### all mapsets successfully build! #######")
printinfo("")
printinfo("")

quit()
