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

            basemap - to route  motorvehicle, bicycle and foot
            bikemap - better visibiltity of cycleroute and -ways
            carmpap - only for motorvehicle, no routing for bicycle and foot


            FIXME (possible)
            Contourlines (possible)

            These Styles, based and inspired by the AIO-Style,
            are Public Domain, do what you want with them.

            Place your own *-poly in WORK_DIR/poly,
            example for dach, use dach.poly as name
        '''))

parser.add_argument('-b', '--buildmap', dest='buildmap', default=config.get('mapset', 'default'))
parser.add_argument('-c', '--contourlines', action="store_true", help="create contourlines layer")
parser.add_argument('-al', '--areas_list', action="store_true", help="use areas.list to split mapdata")
parser.add_argument('-cs', '--check_styles', action="store_true", help="test the styles")
parser.add_argument('-l', '--log', action="store_true", help="enable mkgmaps log")
parser.add_argument('-lm', '--list_mapstyle', action="store_true")
parser.add_argument('-s', '--map_set', dest='map_set', default='no', help="set $MAP_SET as new default")
parser.add_argument('-a', '--add_style', dest='add_style', default='no')
parser.add_argument('-m', '--map_style', dest='map_style', default='no', help="enable/disable a style")
parser.add_argument('-r', '--rm_style', dest='rm_style', default='no')
parser.add_argument('--print_config', action="store_true", help="printout the config sections  and exit")
parser.add_argument('--print_section', dest='print_section', default='no', help="printout a config section and exit")
parser.add_argument('-v', '--verbose', action="store_true", help="increase verbosity")
parser.add_argument('-z', '--zip_img', action="store_true", help="enable zipping the images")
parser.add_argument('--svn', action="store_true", help="use svn versions of splitter and mkgmap")

args = parser.parse_args()

"""
edit map_styles list

"""

if (args.print_config):
  print()
  printinfo("this are the sections of pygmap3.cfg: ")
  print()
  sections = config.sections()
  for i in (sections):
    print("  " + (i))
  print()
  printinfo("to get more infos about a section use")
  printinfo("    pygmap3.py -ps $SECTION   ")
  quit()

if (args.print_section) != "no":
  print()
  printinfo("this is the " + (args.print_section) +  " section of pygmap3.cfg: ")
  print()
  for key in (config[(args.print_section)]):
    print ("  " + (key) + " = " + config[(args.print_section)][(key)])
  print()
  quit()

if (args.list_mapstyle):
  if config.has_section('map_styles') == True:
    print()
    printinfo("map_styles list includes: ")
    for key in (config['map_styles']):
      print ("  " + (key) + " = " + config['map_styles'][(key)])
    print()
    printinfo("mapset list includes: ")
    for key in (config['mapset']):
      print ("  " + (key) + " = " + config['mapset'][(key)])
    print()
  quit()

if (args.add_style) != "no":
  if os.path.exists("mystyles/" + (args.add_style) + "_style") == False:
    printerror((args.add_style) + "_style - dir not found")
    quit()
  if (args.add_style) != "defaultmap":
    if os.path.exists("mystyles/" + (args.add_style) + "_typ.txt") == False:
      printerror((args.add_style) + "_typ.txt not found")
      quit()
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
  if os.path.exists("mystyles/" + (args.map_style) + "_style") == False:
    print()
    printerror((args.map_style) + "_style - dir not found")
    printerror("possible styles are: ")
    print()
    print("    basemap")
    print("    bikemap")
    print("    fixme")
    print("    defaultmap")
    print("    carmpp")
    print()
    print()
    quit()
  if config.has_option('map_styles', (args.map_style)) == True:
    if (args.map_style) != "defaultmap":
      if os.path.exists("mystyles/" + (args.map_style) + "_typ.txt") == False:
        printerror((args.map_style) + "_typ.txt not found")
        quit()
    if config.get('map_styles', (args.map_style)) == "yes":
      config.set('map_styles', (args.map_style), 'no')
      printwarning((args.map_style) + " style disabled")
    elif config.get('map_styles', (args.map_style)) == "no":
      config.set('map_styles', (args.map_style), 'yes')
      printinfo((args.map_style) + " style enabled")
  else:
     config.set('map_styles', (args.map_style), 'yes')
     printinfo((args.map_style) + " style added and enabled")

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

if (args.check_styles):
  import check_styles
  check_styles.check()
  quit()


if ('runtime' in config) == True:
  config.remove_section('runtime')
  write_config()

config.add_section('runtime')

"""
set buildmap

"""
config.set('runtime', 'buildmap', (args.buildmap))

"""
verbosity

"""

if (args.verbose):
  config.set('runtime', 'verbose', 'yes')
  printinfo("verbosity turned on")
else:
  config.set('runtime', 'verbose', 'no')

write_config()

buildmap = config.get('runtime', 'buildmap')

ExitCode = os.path.exists("poly/" + (buildmap) + ".poly")
if ExitCode == False:
  print()
  printerror((WORK_DIR) + "poly/" + (buildmap) + ".poly not found... ")
  printerror("please create or download "+ (buildmap) + ".poly")
  quit()


"""
read the config and set or create the mapid

"""

if config.has_option('mapid', (buildmap)) == True:
  option_mapid = config.get('mapid', (buildmap))
else:
  option_mapid = config.get('mapid', 'next_mapid')
  next_mapid = str(int(option_mapid)+1)
  config.set('mapid', (buildmap), (option_mapid))
  config.set('mapid', 'next_mapid', (next_mapid))
  write_config()

write_config()



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
if (args.svn):
  config.set('runtime', 'svn', 'yes')
  print()
  printwarning("using svn versions of splitter and mkgmap")

  write_config()

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
if ExitCode == True:
  try:
    description = (buildmap) + "_" + config.get('time_stamp', (buildmap))
    printinfo(description)
  except:
    printerror()
    printerror()
    printerror("keep_data.lck found and no older time_stamp for " + (buildmap) + " is set in config")
    printerror("please remove keep_data.lck with 'keep_data.py'")
    printerror()
    quit()

else:
  buildmap_o5m = (WORK_DIR) + "o5m/" + (buildmap) +  ".o5m"

  """
  create mapdata if needed

  """
  import mapdata

  ExitCode = os.path.exists(buildmap_o5m)
  if ExitCode == False:
    ExitCode = os.path.exists("o5m/planet.o5m")
    if ExitCode == False:
      printerror()
      printerror("No Planet-File found!  ")
      printerror()
      printerror("A planet is needed,because you didn't have ")
      printerror("a " + (buildmap) + ".o5m O5M-File! ")
      printerror("Please download one with 'planet_up.py'.")
      printerror()
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

  if (args.areas_list):
    if config.get('splitter', 'use_areas') == "no":
      config.set('splitter', 'use_areas', 'yes')
      print()
      printinfo("use_areas enabled in config file")
      print()
      write_config()

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
if (args.log):
  config.set('mkgmap', 'logging', 'yes')
  write_config()

import mkgmap
mkgmap.render()

if config.get('mkgmap', 'logging') == "yes":
  config.set('mkgmap', 'logging', 'no')
  write_config()

"""
zip the images, kml and log
"""

import store

if (args.zip_img):
  store.zip_img()
  store.kml()

if config.get('mkgmap', 'logging') == "yes":
  store.log()

"""
create the contourlines

"""

if (args.contourlines):
    ExitCode = os.path.exists("mystyles/contourlines_style")
    if ExitCode == True:
      import contourlines
      contourlines.create_cont()
    else:
      printwarning("dir mystyles/contourlines_style not found")

print()
print()
print("  ---------- " + (buildmap) + " ready! ----------")
print()
print()

quit()


"""

## Changelog

v0.9.49 - update only the needed mapdata with osmupdate
          move planet to $WORK_DIR/o5m

v0.9.48 - add 7z as output for the images
        - mapid for DACH and germany


"""

