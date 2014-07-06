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
__version__ = "0.9.50"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2014 Bernd Weigelt"
__credits__ = "Franco B."
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

ExitCode = os.path.exists("pygmap3.cfg")
if ExitCode == True:
  ExitCode = os.path.exists("pygmap3.cfg.bak")
  if ExitCode == True:
    os.remove("pygmap3.cfg.bak")

  shutil.copyfile('pygmap3.cfg', 'pygmap3.cfg.bak')


"""
create dir o5m, areas, poly and tiles

"""

for dir in ['o5m', 'areas', 'poly', 'tiles']:
  ExitCode = os.path.exists(dir)
  if ExitCode == False:
    os.mkdir(dir)

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

            map layers (routable):
            basemap - to route  motorvehicle, bicycle and foot
            bikemap - better visibiltity of cycleroute and -ways
            carmap  - only for motorvehicle, no routing for bicycle and foot

            additional layers
            fixme   - a fixme layer for mapping
            housenumbers - a layer that shows the housenumbers

            Place your own *-poly in WORK_DIR/poly,
            example for dach, use dach.poly as name
        '''))

# mapset handling
parser.add_argument('-b', '--buildmap', dest='buildmap', default=config.get('runtime', 'default'), help="set map region to build, default is " + config.get('runtime', 'default'))
parser.add_argument('-s', '--set_default', dest='set_default', default='no', help="set region to build as new default")

# list styles
parser.add_argument('-lm', '--list_mapstyle', action="store_true", help="list the style settings")

# mapstyle handling
parser.add_argument('-a', '--add_style', dest='add_style', default='no', help="add a new style")
parser.add_argument('-m', '--map_style', dest='map_style', default='no', help="enable/disable a style")
parser.add_argument('-r', '--rm_style', dest='rm_style', default='no', help="remove a style")
parser.add_argument('-am', '--all_map_styles', action="store_true", help="enable all map_styles")

# mapdata
parser.add_argument('-k', '--keep_data', action="store_true", help="don't update the mapdata")

# config
parser.add_argument('-pc', '--print_config', action="store_true", help="printout the config sections  and exit")
parser.add_argument('-ps', '--print_section', dest='print_section', default='no', help="printout a config section and exit")

# splitter options
parser.add_argument('-al', '--areas_list', action="store_true", help="use areas.list to split mapdata")
parser.add_argument('-ns', '--no_split', action="store_true", help="don't split the mapdata")

# contourlines
parser.add_argument('-c', '--contourlines', action="store_true", help="create contourlines layer")

# image handling
parser.add_argument('-z', '--zip_img', action="store_true", help="enable zipping the images")

# Java options
parser.add_argument('-rs', '--ramsize', dest='ramsize', default='3G', help="set the ramsize for Java, default is 3G")

# maxnodes
parser.add_argument('-mn', '--maxnodes', dest='maxnodes', default='1600000', help="set the maxnodes count for splitter")

# debugging
parser.add_argument('-cs', '--check_styles', action="store_true", help="test the styles")
parser.add_argument('-st', '--stop_after', dest='stop_after', default='no', help='buildprocess stop after [tests|create|splitter|mkgmap]')
parser.add_argument('-v', '--verbose', action="store_true", help="increase verbosity")
parser.add_argument('-l', '--log', action="store_true", help="enable splitter and mkgmap logging")

# development
parser.add_argument('--svn', action="store_true", help="use svn versions of splitter and mkgmap")

args = parser.parse_args()

# config options

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


# map build options

if (args.areas_list):
  if config.get('runtime', 'use_areas') == "no":
    config.set('runtime', 'use_areas', 'yes')
    print()
    printinfo("use_areas enabled in config file")
    print()

  elif config.get('runtime', 'use_areas') == "yes":
    config.set('runtime', 'use_areas', 'no')
    print()
    printinfo("use_areas disabled in config file")
    print()

  write_config()
  quit()

if (args.list_mapstyle):
  if config.has_section('map_styles') == True:
    print()
    printinfo("map_styles list includes: ")
    print()
    for key in (config['map_styles']):
      print("  " + (key) + " = " + config['map_styles'][(key)])
    if config.has_section('mapset') == True:
      print()
      printinfo("mapset list includes: ")
      print()
      for key in (config['mapset']):
        print("  " + (key) + " = " + config['mapset'][(key)])
  print()
  quit()

if (args.all_map_styles):
  if config.has_section('map_styles') == True:
    for key in (config['map_styles']):
      config.set('map_styles', (key), 'yes')
      print ("  " + (key) + " = " + config['map_styles'][(key)])

    write_config()
    print()
    printinfo("all mapstyles enabled")
    print()
  quit()

if (args.add_style) != "no":
  if os.path.exists("styles/" + (args.add_style) + "_style") == True:
    config.set('map_styles', (args.add_style), 'yes')
    printinfo((args.add_style) + " added to map_styles list")
  else:
    print()
    printerror((args.add_style) + "_style - dir not found")
  print()  
  quit()

if (args.map_style) != "no" and (args.map_style) != "defaultmap":
  if os.path.exists("styles/" + (args.map_style) + "_style") == False:
    print()
    printerror((args.map_style) + "_style - dir not found")
    printerror("possible styles are: ")
    print()
    print("    basemap")
    print("    bikemap")
    print("    carmap")
    print("    boundary")
    print("    housenumber")
    print("    fixme")
    print("    defaultmap")
    print("    or your own style!")
    print()
    quit()

if (args.map_style) != "no":
  if config.has_option('map_styles', (args.map_style)) == True:
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

if (args.rm_style) != "no":
  if config.has_option('map_styles', (args.rm_style)) == True:
    config.remove_option('map_styles', (args.rm_style))
  printinfo((args.rm_style) + " removed from map_styles list")
  quit()

if (args.set_default) != "no":
  ExitCode = os.path.exists("poly/" + (args.set_default) + ".poly")
  if ExitCode == False:
    print()
    printerror((WORK_DIR) + "poly/" + (args.set_default) + ".poly not found... ")
    printerror("please create or download "+ (args.set_default) + ".poly")
    print()
    quit()

  config.set('runtime', 'default', (args.set_default))
  print((args.set_default) + " set as new default region")

  write_config()
  quit()

if (args.check_styles):
  import check_styles
  check_styles.check()
  quit()


# runtime options

"""
ramsize for java
"""

if (args.ramsize) != "3G":
  config.set('runtime', 'ramsize', ("-Xmx" + str(args.ramsize)))

"""
maxnodes for plitter
"""

if (args.maxnodes) != "1600000":
  config.set('runtime', 'maxnodes', ("-Xmx" + str(args.maxnodes)))

"""
logging

"""

if (args.log):
  config.set('runtime', 'logging', 'yes')
else:
  config.set('runtime', 'logging', 'no')

"""
verbosity

"""

if (args.verbose):
  config.set('runtime', 'verbose', 'yes')
  printinfo("verbosity turned on")

"""
development version of splitter and mkgmap

"""

if (args.svn):
  config.set('runtime', 'svn', 'yes')
else:
  config.set('runtime', 'svn', 'no')

"""
set buildmap

"""

buildmap = (args.buildmap)
config.set('runtime', 'buildmap', (buildmap))

"""
set or create the mapid

"""

if config.has_option('mapid', (buildmap)) == True:
  option_mapid = config.get('mapid', (buildmap))
else:
  option_mapid = config.get('mapid', 'next_mapid')
  next_mapid = str(int(option_mapid)+1)
  config.set('mapid', (buildmap), (option_mapid))
  config.set('mapid', 'next_mapid', (next_mapid))

"""
osmupdate and osmconvert

"""

if config.get('osmtools', 'check') == "yes":
  def checkprg(programmtofind, solutionhint):
    ExitCode = os.system("which " + programmtofind)
    if ExitCode == 0:
      printinfo(programmtofind + " found")
    else:
      printerror(programmtofind + " not found")
      print(solutionhint)
      quit()

  for tool in ['osmconvert', 'osmupdate']:
    hint = (tool) + " missed, please use mk_osmtools to build it from sources"
    checkprg((tool), hint)

  config.set('osmtools', 'check', 'no')

"""
write to config

"""

write_config()

"""
get splitter and mkgmap

"""

import get_tools

if config.get('runtime', 'svn') == "yes":
  config.set('runtime', 'svn', 'no')
  write_config()

"""
bounds and precomp_sea from navmap.eu

"""

if config.get('navmap', 'pre_comp') == "yes":
  import navmap

"""
--stop_after tests

"""

if (args.stop_after) == "tests":
  print()
  printinfo("Tests successful finished")
  print()
  quit()

"""
mapdata to use

"""

buildmap_o5m = (WORK_DIR) + "o5m/" + (buildmap) +  ".o5m"


"""
if --keep_data is set, then use the old data

"""

if (args.keep_data) == False:

  import mapdata

  ExitCode = os.path.exists(buildmap_o5m)
  if ExitCode == False:

    mapdata.create_o5m()

  """
  update mapdata

  """

  mapdata.update_o5m()

os.chdir(WORK_DIR)
config.read('pygmap3.cfg')

"""
--stop_after create

"""

if (args.stop_after) == "create":
  print()
  printinfo(" Mapdata for " + (buildmap) + " successful extracted/updated")
  print()
  quit()


"""
split mapdata

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

if (args.no_split):
  if (args.verbose):
    print()
    printinfo("no_split switched on!")
  ExitCode = os.path.exists((WORK_DIR) + "tiles/" + (buildmap) + "_split.ready")
  if ExitCode == False:
    print()
    printwarning("can't find tiles/" + (buildmap) + "_split.ready")
    printwarning("--no_split/-ns makes no sense, ignoring it")
    splitter.split()

else:
  remove_old_tiles()
  os.chdir(WORK_DIR)
  print()
  printinfo("now splitting the mapdata...")
  splitter.split()

"""
--stop_after splitter

"""

if (args.stop_after) == "splitter":
  print()
  printinfo((buildmap) + ".o5m successful splitted")
  print()
  quit()

"""
render the map-images

"""

import mkgmap
mkgmap.render()

if config.get('runtime', 'logging') == "yes":
  config.set('runtime', 'logging', 'no')
  write_config()


"""
--stop_after mkgmap

"""

if (args.stop_after) == "mkgmap":
  print()
  printinfo(" Mapset for " + (buildmap) + " successful created")
  print()
  quit()

"""
zip the images, kml and log
"""

import store

if (args.zip_img):
  store.zip_img()
  store.kml()

if(args.log):
  store.log()

"""
create the contourlines

"""

if (args.contourlines):
    ExitCode = os.path.exists("styles/contourlines_style")
    if ExitCode == True:
      import contourlines
      contourlines.create_cont()
    else:
      printwarning("dir styles/contourlines_style not found")

print()
print()
print("  ---------- " + (buildmap) + " ready! ----------")
print()
print()

quit()


