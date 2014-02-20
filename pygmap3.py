#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
version 3 as published by the Free Software Foundation.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.
You should have received a copy of this license along
with this program; if not, see http://www.gnu.org/licenses/.


"""
__version__ = "0.9.49"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2013 Bernd Weigelt"
__credits__ = "Dschuwa, Franco B."
__license__ = "AGPLv3"
__maintainer__ = "Bernd Weigelt"
__email__ = "weigelt.bernd@web.de"
__status__ = "RC"

"""
pygmap3.py, a script to build maps for GARMIN PNAs

Work in progress, be sure, that you ran it in
the knowledge, that it can be harmful for your data,
but i hope, it's safe.


Following Software is needed.

Please install them manually, they have to be
compiled on your system:

osmconvert
http://wiki.openstreetmap.org/wiki/Osmconvert
osmupdate
http://wiki.openstreetmap.org/wiki/Osmupdate

phyghtmap (to create the contourlines)
http://katze.tfiu.de/projects/phyghtmap/


Tools will be installed by the script:

mkgmap and splitter from
http://www.mkgmap.org.uk
and some other things

This files should downloaded manually
precomp_sea from navmap.org
boundaries from navmap.org

"""

import sys
import os
import datetime
import argparse
import configparser
import time
import urllib.request
import shutil

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
test if a file or dir can be found at a predefined place
raise message if fails and returns 1
on success return 0
"""

ExitCode = os.path.exists(WORK_DIR)
if ExitCode == False:
  printerror("Please create" + (WORK_DIR))
  quit()

os.chdir(WORK_DIR)

ExitCode = os.path.exists("planet.o5m")
if ExitCode == True:
  printerror("please move planet.o5m to " + (WORK_DIR) + "o5m/")
  quit()

ExitCode = os.path.exists("pygmap3.cfg")
if ExitCode == True:
  ExitCode = os.path.exists("pygmap3.cfg.bak")
  if ExitCode == True:
    os.remove("pygmap3.cfg.bak")

  shutil.copyfile('pygmap3.cfg', 'pygmap3.cfg.bak')

"""
configparser

"""

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

config = configparser.ConfigParser()

"""
create a new config if needed

"""

import build_config

ExitCode = os.path.exists("pygmap3.cfg")
if ExitCode == False:
  build_config.create()

"""
update the config if needed

"""

build_config.update()

config.read('pygmap3.cfg')


"""
argparse

"""

parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\

            To build maps for Garmin PNA

            Basemap
            Bikemap
            FIXME (possible)
            Contourlines (possible)

            This Style, based and inspired by the AIO-Style,
            is Public Domain, do what you want with it.


            ############################
            These Mapstyles are not included, they have to installed manually:
            The RRK-Style is CC-BY 2.0 --> http://www.aighes.de/OSM/index.php
            The FZK-Style is copyrighted by Klaus Tockloth
            ############################


            Place your own *-poly in WORK_DIR/poly,
            example for dach, use dach.poly as name


            -b hamburg
            -b bayern
            -b germany
            -b dach (default)
            -s $MAPSET          set $MAPSET as new default

            to create different Mapstyles

            -m bikemap          enable/disbale bikemap style
            -m list             list the possible map_styles
            -a $NEW_STYLE       add a new style to list
            -r $STYLE           remove style from list

        '''))

parser.add_argument('-b', '--buildmap', dest='buildmap', default=config.get('mapset', 'default'))
parser.add_argument('-s', '--map_set', dest='map_set', default='no')
parser.add_argument('-m', '--map_style', dest='map_style', default='no')
parser.add_argument('-a', '--add_style', dest='add_style', default='no')
parser.add_argument('-r', '--rm_style', dest='rm_style', default='no')

args = parser.parse_args()

"""
edit map_styles list

"""

if (args.map_style) == "list":
  if config.has_section('map_styles') == True:
    printinfo("map_styles list includes: ")
    for key in (config['map_styles']):
      print ("  " + (key) + " = " + config['map_styles'][(key)])
  else:
    printwarning("map_styles list not found")
  quit()

if (args.add_style) != "no":
  if config.has_option('map_styles', (args.add_style)) == False:
    config.set('map_styles', (args.add_style), 'yes')
    write_config()
  printinfo((args.add_style) + " added to map_styles list")
  quit()

if (args.rm_style) != "no":
  if config.has_option('map_styles', (args.rm_style)) == True:
    config.remove_option('map_styles', (args.rm_style))
    write_config()
  printwarning((args.rm_style) + " removed from map_styles list")
  quit()

if (args.map_style) != "no":
  if config.has_option('map_styles', (args.map_style)) == True:
    if config.get('map_styles', (args.map_style)) == "yes":
      config.set('map_styles', (args.map_style), 'no')
      printwarning((args.map_style) + " style disabled")
    elif config.get('map_styles', (args.map_style)) == "no":
      config.set('map_styles', (args.map_style), 'yes')
      printinfo((args.map_style) + " style enabled")
    write_config()
    quit()

if (args.map_set) != "no":
  ExitCode = os.path.exists("poly/" + (args.map_set) + ".poly")
  if ExitCode == False:
    printerror((WORK_DIR) + "poly/" + (args.map_set) + ".poly not found... ")
    printerror("please create or download "+ (args.map_set) + ".poly")
    quit()
  config.set('mapset', 'default', (args.map_set))
  print((args.map_set) + " set as new default mapset")
  write_config()
  quit()

config.read('pygmap3.cfg')

if ('runtime' in config) == True:
  config.remove_section('runtime')
  write_config()

config.add_section('runtime')

"""
set buildmap

"""
config.set('runtime', 'buildmap', (args.buildmap))
write_config()


config.read('pygmap3.cfg')

buildmap = config.get('runtime', 'buildmap')

ExitCode = os.path.exists("poly/" + (buildmap) + ".poly")
if ExitCode == False:
  printerror((WORK_DIR) + "poly/" + (buildmap) + ".poly not found... ")
  printerror("please create or download "+ (buildmap) + ".poly")
  quit()


"""
read the config and set or create the mapid

"""
config.read('pygmap3.cfg')

if config.has_option('mapid', (buildmap)) == True:
  option_mapid = config.get('mapid', (buildmap))
else:
  option_mapid = config.get('mapid', 'next_mapid')
  next_mapid = str(int(option_mapid)+1)
  config.set('mapid', (buildmap), (option_mapid))
  config.set('mapid', 'next_mapid', (next_mapid))
  write_config()

write_config()

config.read('pygmap3.cfg')


"""
create dir for areas. poly and splitter-output

"""

for dir in ['o5m', 'areas', 'poly', 'tiles']:
  ExitCode = os.path.exists(dir)
  if ExitCode == False:
    os.mkdir(dir)


"""
get splitter and mkgmap

"""

import get_tools


"""
bounds and precomp_sea from navmap.eu

"""

if config.get('navmap', 'pre_comp') == "yes":
  import navmap


"""
is there a keep_data.lck, then use the old data

"""

ExitCode = os.path.exists("keep_data.lck")
if ExitCode == False:

  buildmap_o5m = (WORK_DIR) + "o5m/" + (buildmap) +  ".o5m"

  """
  create mapdata if needed

  """
  import mapdata

  ExitCode = os.path.exists(buildmap_o5m)
  if ExitCode == False:
    ExitCode = os.path.exists("o5m/planet.o5m")
    if ExitCode == False:
      printerror("")
      printerror("No Planet-File found!  ")
      printerror("")
      printerror("A planet is needed,because you didn't have ")
      printerror("a " + (buildmap) + ".o5m O5M-File! ")
      printerror("Please download one with 'planet_up.py'.")
      printerror("")
      printerror("The first planet will be updated by 'planet_up.py', ")
      printerror("but the extracted mapdata can be updated with ")
      printerror("'pygmap3.py', this function ist enabled by default ")
      printerror("disable it with 'keep_data.py'. ")
      printerror("'HINT: 'keep_data.py' is a FlipFlop. ")
      quit()


    mapdata.create_o5m()

  """
  update mapdata

  """

  mapdata.update_o5m()


os.chdir(WORK_DIR)
config.read('pygmap3.cfg')

description = (buildmap) + "_" + config.get('time_stamp', (buildmap))
printinfo(description)


"""
split rawdata

"""


def remove_old_tiles():
  path = 'tiles'
  for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
      try:
        os.remove(os.path.join(path, file))
      except:
        print('Could not delete', file, 'in', path)

import splitter

ExitCode = os.path.exists((WORK_DIR) + "no_split.lck")
if ExitCode == False:
  remove_old_tiles()

  os.chdir(WORK_DIR)

  splitter.split()

elif ExitCode == True:
  printwarning("no_split switched on!")
  ExitCode = os.path.exists((WORK_DIR) + "tiles/" + (buildmap) + "_split.ready")
  if ExitCode == False:
    printwarning("have to split once again!")
    remove_old_tiles()

    os.chdir(WORK_DIR)

    splitter.split()


"""
render the map-images

"""
import mkgmap
mkgmap.render()


"""
zip the images, kml and log
"""

import store

store.zipp()

store.kml()

if config.get('mkgmap', 'logging') == "yes":
  store.log()

"""
create the contourlines

"""

if config.get('contourlines', 'build') == "yes":
  import contourlines
  contourlines.create_cont()


printinfo("")
printinfo("")
printinfo("############### " + (buildmap) + " ready! ###############")
printinfo("")
printinfo("")

quit()


"""

## Changelog

v0.9.49 - update only the needed mapdata with osmupdate
          move planet to $WORK_DIR/o5m

v0.9.48 - add 7z as output for the images
        - mapid for DACH and germany


"""

