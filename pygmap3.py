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

## local modules
import build_config
import get_tools
import navmap
import geonames
import splitter
import mkgmap
import store

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

if os.path.exists(WORK_DIR) == False:
  print()
  printerror("Please create " + WORK_DIR)
  print()
  quit()

os.chdir(WORK_DIR)

if os.path.exists("pygmap3.cfg") == True:
  if os.path.exists("pygmap3.cfg.bak") == True:
    os.remove("pygmap3.cfg.bak")

  shutil.copyfile('pygmap3.cfg', 'pygmap3.cfg.bak')


"""
create dir o5m, areas, poly and tiles

"""

for dir in ['o5m', 'areas', 'poly', 'tiles']:
  if os.path.exists(dir) == False:
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

if os.path.exists("pygmap3.cfg") == False:
  build_config.create()

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
            bikemap - better visibility of cycleroute and -ways
            carmap  - only for motorvehicle, no routing for bicycle and foot

            additional layers
            fixme   - a fixme layer for mapping
            boundary - a layer to show boundaries with admin_level<=6
            housenumbers - a layer to shows the housenumbers

            Place your own *-poly in WORK_DIR/poly,
            example for dach, use dach.poly as name

        '''))

# mapset handling
parser.add_argument('-b', '--buildmap', dest='buildmap', default=config['runtime']['default'], help="set map region to build, default is " + config['runtime']['default'])
parser.add_argument('-s', '--set_default', dest='set_default', default='no', help="set region to build as new default")
parser.add_argument('-ntl', '--name-tag-list', dest='name_tag_list', default='no', help="which name tag should be used for naming objects, example 'name:en,name:int,name'")

# list styles
parser.add_argument('-lm', '--list_mapstyle', action="store_true", help="list the style settings")

# mapstyle handling
parser.add_argument('-a', '--add_style', dest='add_style', default='no', help="add a new style")
parser.add_argument('-m', '--map_style', dest='map_style', default='no', help="enable/disable a style")
parser.add_argument('-r', '--rm_style', dest='rm_style', default='no', help="remove a style")
parser.add_argument('-am', '--all_map_styles', action="store_true", help="enable all map_styles")
parser.add_argument('-dm', '--no_map_styles', action="store_true", help="disable all map_styles")

# mapdata
parser.add_argument('-k', '--keep_data', action="store_true", help="don't update the mapdata")
parser.add_argument('-ob', '--old_bounds', action="store_true", help="use the previous used bounds")

# config
parser.add_argument('-pc', '--print_config', action="store_true", help="printout the config sections  and exit")
parser.add_argument('-ps', '--print_section', dest='print_section', default='no', help="printout a config section and exit")

# splitter options
parser.add_argument('-na', '--no_areas_list', action="store_true", help=" don't use areas.list to split mapdata")
parser.add_argument('-ns', '--no_split', action="store_true", help="don't split the mapdata")

# mkgmap options

# contourlines
parser.add_argument('-c', '--contourlines', action="store_true", help="create contourlines layer")

# image handling
parser.add_argument('-z', '--zip_img', action="store_true", help="enable zipping the images")

# Java options
parser.add_argument('-rs', '--ramsize', dest='ramsize', default=config['runtime']['ramsize'], help="set the ramsize for Java, example '3G' or '3000M'")

# maxnodes
parser.add_argument('-mn', '--maxnodes', dest='maxnodes', default=config['runtime']['maxnodes'], help="set the maxnodes count for splitter")

# debugging
parser.add_argument('-cs', '--check_styles', action="store_true", help="test the styles")
parser.add_argument('-st', '--stop_after', dest='stop_after', default='no', help='buildprocess stop after [get_tools|contourlines|mapdata|splitter|mkgmap]')
parser.add_argument('-v', '--verbose', action="store_true", help="increase verbosity")
parser.add_argument('-l', '--log', action="store_true", help="enable splitter and mkgmap logging")

# development
parser.add_argument('-mt', '--mkgmap_test', action="store_true", help="use the svn version of mkgmap like housenumbers2")
parser.add_argument('-ms', '--mkgmap_set', dest='mkgmap_set', default='no', help="set the svn version of mkgmap like housenumbers2")

args = parser.parse_args()


"""
set buildmap

"""

buildmap = args.buildmap
config.set('runtime', 'buildmap', buildmap)

name_tag_list = args.name_tag_list

if ('name_tag_list' in config) == False:
  config.add_section('name_tag_list')
  config.set('name_tag_list', 'default', 'name:en,name:int,name')
  write_config()

if config.has_option('name_tag_list', buildmap) == False:
  print()
  printwarning("for this mapset isn't set the MKGMAP option '--name-tag-list'")
  printwarning("using the default 'name:en,name:int,name'")
  print()
  
if args.name_tag_list != "no":
  config.set('name_tag_list', buildmap, name_tag_list) 

# config options

if args.print_config:
  print()
  printinfo("this are the sections of pygmap3.cfg: ")
  print()
  sections = config.sections()
  for i in (sections):
    print("  " + (i))
  print()
  printinfo("to get more infos about a section use")
  print("    pygmap3.py -ps $SECTION   ")
  quit()

if args.print_section != "no":
  print()
  printinfo("this is the " + args.print_section +  " section of pygmap3.cfg: ")
  print()
  for key in (config[args.print_section]):
    print ("  " + key + " = " + config[args.print_section][key])
  print()
  quit()

# map build options

if args.list_mapstyle:
  if config.has_section('map_styles') == True:
    print()
    printinfo("map_styles list includes: ")
    print()
    for key in (config['map_styles']):
      print("  " + (key) + " = " + config['map_styles'][key])
    if config.has_section('mapset') == True:
      print()
      printinfo("mapset list includes: ")
      print()
      for key in (config['mapset']):
        print("  " + key + " = " + config['mapset'][key])
  print()
  quit()

if args.all_map_styles:
  if config.has_section('map_styles') == True:
    print()
    for key in (config['map_styles']):
      config.set('map_styles', key, 'yes')
      print ("  " + key + " = " + config['map_styles'][key])

    write_config()
    print()
    printinfo("all mapstyles enabled")
    print()
  quit()

if args.no_map_styles:
  if config.has_section('map_styles') == True:
    print()
    for key in (config['map_styles']):
      config.set('map_styles', key, 'no')
      print ("  " + key + " = " + config['map_styles'][key])

    write_config()
    print()
    printinfo("all mapstyles disabled,")
    printinfo("please enable at least one mapstyle before the next build")
    printinfo("as example 'pygmap3.py -m basemap'")
    print()
  quit()

def info_styles():
  print()
  printerror(args.add_style + "_style - dir not found")
  print()
  print()
  printinfo("possible styles for routable layers are: ")
  print("    basemap")
  print("    bikemap")
  print("    carmap")
  print()
  print("    defaultmap")
  print()
  printinfo("possible styles as overlays are:")
  print("    bikeroute")
  print("    boundary")
  print("    housenumber")
  print("    fixme")
  print()
  print()
  print("    or your own style files!")
  print()

if args.add_style != "no":
  if os.path.exists("styles/" + args.add_style + "_style") == True:
    config.set('map_styles', args.add_style, 'yes')
    print()
    if args.add_style in config == False:
      printinfo("please add a section [" + args.add_style + "] to pygmap3.cfg")
      print("see the existing entries for the fixme layer as example")
      print("for family-id and product-id increase the values")
      print("mapid_ext and draw_priotity could be the same values")
      print("family_name is a free text value")
      print()
      printinfo("please read mkgmap's manual for more infos")
      print()
      print("  [fixme]")
      for key in config['fixme']:
        print("  " + key + " = " + config['fixme'][key])
      print()
    printinfo(args.add_style + " added to map_styles list")
  elif args.add_style == "defaultmap":
    config.set('map_styles', args.add_style, 'yes')
  else:
    info_styles()
  print()
  write_config()
  quit()

if args.map_style != "no" and args.map_style != "defaultmap":
  if os.path.exists("styles/" + args.map_style + "_style") == False:
    info_styles()
    quit()

if args.map_style != "no":
  if config.has_option('map_styles', args.map_style) == True:
    if config['map_styles'][args.map_style] == "yes":
      config.set('map_styles', args.map_style, 'no')
      print()
      printwarning(args.map_style + " style disabled")
    elif config['map_styles'][args.map_style] == "no":
      config.set('map_styles', args.map_style, 'yes')
      print()
      printinfo(args.map_style + " style enabled")
  else:
     config.set('map_styles', args.map_style, 'yes')
     print()
     printinfo(args.map_style + " style added and enabled")

  write_config()
  quit()

if args.rm_style != "no":
  if config.has_option('map_styles', args.rm_style) == True:
    config.remove_option('map_styles', args.rm_style)
    write_config()
  print()
  printinfo(args.rm_style + " removed from map_styles list")
  print()
  quit()

if args.set_default != "no":
  if os.path.exists("poly/" + args.set_default + ".poly") == False:
    print()
    printerror((WORK_DIR) + "poly/" + args.set_default + ".poly not found... ")
    printerror("please create or download "+ args.set_default + ".poly")
    print()
    quit()

  config.set('runtime', 'default', args.set_default)
  print(args.set_default + " set as new default region")

  write_config()
  quit()

if args.check_styles:

  mkgmap.check()
  quit()

# runtime options

"""
ramsize for java
"""

if args.ramsize != config['runtime']['ramsize']:
  config.set('runtime', 'ramsize', "-Xmx" + str(args.ramsize))

"""
maxnodes for splitter
"""

if args.maxnodes != config['runtime']['maxnodes']:
  config.set('runtime', 'maxnodes', args.maxnodes)
  if os.path.exists("areas/" + buildmap + "_areas.list"):
    os.remove("areas/" + buildmap + "_areas.list")

"""
don't use the areas.list

"""

if args.no_areas_list:
  if os.path.exists("areas/" + buildmap + "_areas.list"):
    os.remove("areas/" + buildmap + "_areas.list")

"""
logging

"""

if args.log:
  config.set('runtime', 'logging', 'yes')
else:
  config.set('runtime', 'logging', 'no')

"""
verbosity

"""

if args.verbose:
  config.set('runtime', 'verbose', 'yes')
else:
  config.set('runtime', 'verbose', 'no')

"""
development version of splitter and mkgmap

"""

config.set('runtime', 'use_mkgmap_test', 'no')

if args.mkgmap_set != "no":
  config.set('runtime', 'mkgmap_test', args.mkgmap_set)
  config.set('runtime', 'use_mkgmap_test', 'yes')

if args.mkgmap_test:
  if config.has_option('runtime', 'mkgmap_test'):
    config.set('runtime', 'use_mkgmap_test', 'yes')
  else:
    print()
    printwarning("no test version of mkgmap is set in config")
    printwarning("please use '-ms/--mkgmap_set' to set one version")
    print()
    quit()

"""
set or create the mapid

"""

if config.has_option('mapid', buildmap) == True:
  option_mapid = config['mapid'][buildmap]
else:
  option_mapid = config['mapid']['next_mapid']
  next_mapid = str(int(option_mapid)+1)
  config.set('mapid', buildmap, option_mapid)
  config.set('mapid', 'next_mapid', next_mapid)

"""
osmupdate and osmconvert

"""

if config['osmtools']['check'] == "yes":
  def checkprg(programmtofind, solutionhint):
    if os.system("which " + programmtofind) == 0:
      print()
      printinfo(programmtofind + " found")
    else:
      print()
      printerror(programmtofind + " not found")
      print(solutionhint)
      quit()

  for tool in ['osmconvert', 'osmupdate']:
    hint = tool + " missed, please use mk_osmtools to build it from sources"
    print()
    checkprg(tool, hint)

  config.set('osmtools', 'check', 'no')

write_config()

"""
get splitter and mkgmap

"""

get_tools.from_mkgmap_org()

config.read('pygmap3.cfg')


"""
create the contourlines

"""

if args.contourlines:
    if os.path.exists("styles/contourlines_style") == True:
      import contourlines
      contourlines.create_cont()

    else:
      printwarning("dir styles/contourlines_style not found")

if args.stop_after == "contourlines":
  print()
  printinfo("stop after contourlines creation")
  print()
  quit()

"""
get the geonames file

"""

geonames.cities15000()

"""
bounds and precomp_sea from osm2.pleiades.uni-wuppertal.de

"""

navmap.get_bounds()

"""
--stop_after get_tools

"""

if args.stop_after == "get_tools":
  print()
  printinfo("needed programs found and files successfully loaded")
  print()
  quit()

"""
mapdata to use

if --keep_data is set, then use the old data

"""

os.chdir(WORK_DIR)

if args.keep_data == False:
  import mapdata

  if os.path.exists("o5m/" + buildmap + ".o5m") == False:
    mapdata.create_o5m()

  """
  update mapdata

  """

  mapdata.update_o5m()

os.chdir(WORK_DIR)
config.read('pygmap3.cfg')

"""
--stop_after mapdata

"""

if args.stop_after == "mapdata":
  print()
  printinfo(" Mapdata for " + buildmap + " " + config['time_stamp'][buildmap] + " successful extracted/updated")
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

if args.no_split:
  if os.path.exists(WORK_DIR + "tiles/" + buildmap + "_split.ready") == False:
    print()
    printwarning("can't find tiles/" + buildmap + "_split.ready")
    print("--no_split/-ns makes no sense, ignoring it")
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

if args.stop_after == "splitter":
  print()
  printinfo(buildmap + ".o5m successful splitted")
  print()
  quit()

"""
render the map-images

"""

mkgmap.render()

if config['runtime']['logging'] == "yes":
  config.set('runtime', 'logging', 'no')
  write_config()


"""
--stop_after mkgmap

"""

if args.stop_after == "mkgmap":
  print()
  printinfo(" Mapset for " + buildmap + " successful created")
  print()
  quit()

"""
zip the images, kml and log
"""



if args.zip_img:
  store.zip_img()
  store.kml()

if args.log:
  store.log()


today = datetime.datetime.now()
DATE = today.strftime('%Y%m%d_%H%M')

print()
print()
print(" ----- " + (DATE) + " ----- " + (buildmap) + " ready! -----")
print()
print()

quit()


