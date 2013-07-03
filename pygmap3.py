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


# own modules

import get_tools
import navmap
import mapdata
import splitter
import mkgmap
import contourlines


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

            additional maps
            RadReiseKarte by Aighes (possible)

            The AIO-Style is Public Domain
            The RRK-Style is CC-BY 2.0 --> http://www.aighes.de/OSM/index.php
            The FZK-Style is copyrighted by Klaus Tockloth

            Place your own *-poly in WORK_DIR/poly,
            example for dach, use dach.poly as name


            Hamburg     --> -b hamburg
            Bayern      --> -b bayern
            Germany     --> -b germany
            D_A_CH      --> -b dach (default)



        '''))

parser.add_argument('-b', '--buildmap', dest='buildmap', default='dach')
args = parser.parse_args()

WORK_DIR = os.environ['HOME'] + "/map_build/"

"""
needed programs und dirs

"""

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)



"""
test if an executable can be found by
following $PATH
raise message if fails and returns 1
on success return 0
search follows $PATH
"""

def checkprg(programmtofind, solutionhint):


  ExitCode = os.system("which " + programmtofind)

  if ExitCode == 0:
    printinfo(programmtofind + " found")
  else:
    printerror(programmtofind + " not found")
    print(solutionhint)


"""
test if a file or dir can be found at a predefined place
raise message if fails and returns 1
on success return 0
"""

def is_there(find, solutionhint):
  ExitCode = os.path.exists(find)

  if ExitCode == True:
     printinfo(find + " found")
  else:
    printerror(find + " not found")
    print(solutionhint)
    quit()



hint = "osmconvert missed, needed to cut data from the planet.o5m"
checkprg("osmconvert", hint)

hint = "osmupdate missed, needed to update the planet.o5m"
checkprg("osmupdate", hint)

hint = "Install: 7z to store the images"
checkprg("7z", hint)

ExitCode = os.path.exists(WORK_DIR)
if ExitCode == False:
  printerror("Please create" + (WORK_DIR))
  quit()

os.chdir(WORK_DIR)

ExitCode = os.path.exists("planet.o5m")
if ExitCode == True:
  printerror("please move planet.o5m to " +(WORK_DIR) + "o5m/")
  printerror("and start the script again!")
  quit()

ExitCode = os.path.exists("fixme_buglayer.conf")
if ExitCode == True:
  printerror(" Please rename 'fixme_buglayer.conf' to 'fixme.conf'")
  quit()

ExitCode = os.path.exists("pygmap3.lck")
if ExitCode == True:
  printwarning("Is there another instance of pygmap3.py running?")

datei = open((WORK_DIR) + "pygmap3.lck", "w")
datei.close()

"""
configparser

"""
def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

config = configparser.ConfigParser()
ExitCode = os.path.exists("pygmap3.cfg")
if ExitCode == False:
  """
  create a default config

  """
  config['DEFAULT'] = {}

  config['ramsize'] = {}
  config['ramsize'] = {'ramsize': '-Xmx3G',}

  config['mapid'] = {}
  config['mapid'] = {'mapid': '6389',}

  config['dach'] = {}
  config['dach'] = {'mapid': '6500',}

  config['germany'] = {}
  config['germany'] = {'mapid': '6501'}

  config['navmap'] = {}
  config['navmap'] = {'bounds': 'yes',}

  config['splitter'] = {}
  config['splitter'] = {'version': 'first_run',
			'logging': 'yes',
                        'latest': 'yes',
                        'maxnodes': '1200000',}

  config['mkgmap'] = {}
  config['mkgmap'] = {'version': 'first_run',
                      'latest': 'yes',
                      'logging': 'no',
                      'check_styles': 'yes',
                      'list_styles': 'no',}

  config['map_styles'] = {}
  config['map_styles'] = {'basemap': 'yes',
			  'bikemap': 'yes',
                          'fixme': 'no',
                          'rrk': 'no',
                          'fzk': 'no',}

  config['basemap'] = {}
  config['basemap'] = {'family-id': '4',
                       'product-id': '45',
                       'family-name': 'Basemap',
                       'draw-priority': '10',
                       'mapid_ext': '1001',}

  config['bikemap'] = {}
  config['bikemap'] = {'family-id': '5',
                       'product-id': '46',
                       'family-name': 'Bikemap',
                       'draw-priority': '10',
                       'mapid_ext': '2001',}

  config['fzk'] = {}
  config['fzk'] = {'family-id': '6276',
                   'product-id': '1',
                   'family-name': 'Freizeitkarte',
                   'draw-priority': '10',
                   'mapid_ext': '3001',}

  config['rrk'] = {}
  config['rrk'] = {'family-id': '1',
                   'product-id': '1000',
                   'family-name': 'RadReiseKarte',
                   'draw-priority': '10',
                   'mapid_ext': '4001',}

  config['fixme'] = {}
  config['fixme'] = {'family-id': '3',
                     'product-id': '33',
                     'family-name': 'OSM-Fixme',
                     'draw-priority': '16',
                     'mapid_ext': '6001',}

  config['contourlines'] = {}
  config['contourlines'] = {'build': 'no'}

  config['store_as'] = {}
  config['store_as'] = {'zip_img': 'no',
                        '7z_img': 'no',}

elif ExitCode == True:
  config.read('pygmap3.cfg')

write_config()

config.read('pygmap3.cfg')

if ('runtime' in config) == True:
  config.remove_section('runtime')
  write_config()
  
if ('planet' in config) == False:
    config.add_section('planet')
    write_config()

config.add_section('runtime')


"""
set buildmap

"""

config.set('runtime', 'buildmap', (args.buildmap))
write_config()

config.read('pygmap3.cfg')

buildmap = config.get('runtime', 'buildmap')

if ((buildmap) in config) == False:
    config.add_section(buildmap)
    write_config()
    
config.read('pygmap3.cfg')

"""
set mapid
example:
[dach]
mapid = 6500

or as default
[mapid]
mapid = 6389

"""

if (config.has_option((buildmap), 'mapid')) == True:
  option_mapid = config.get((buildmap), 'mapid')
else:
  option_mapid = config.get('mapid', 'mapid')

config.set('runtime', 'option_mapid', (option_mapid))
write_config()

config.read('pygmap3.cfg')

"""
create dir for areas. poly and splitter-output

"""

for dir in ['o5m', 'areas', 'poly', 'contourlines', 'tiles']:
  ExitCode = os.path.exists(dir)
  if ExitCode == False:
   os.mkdir(dir)


"""
get splitter and mkgmap

"""

get_tools.get_tools()

"""
bounds and precomp_sea from navmap.eu

"""
navmap.bounds()


"""
get the geonames for splitter

"""

ExitCode = os.path.exists((WORK_DIR) + "cities15000.zip")
if ExitCode == False:
  os.system("wget http://download.geonames.org/export/dump/cities15000.zip")

"""
is there a keep_data.lck, then use the old data

"""

ExitCode = os.path.exists("keep_data.lck")
if ExitCode == False:

  buildmap_o5m = (WORK_DIR) + "o5m/" + (buildmap) +  ".o5m"

  """
  create mapdata if needed

  """
  ExitCode = os.path.exists(buildmap_o5m)
  if ExitCode == False:
    ExitCode = os.path.exists("o5m/planet.o5m")
    if ExitCode == False:
      printerror("No Planet-File found! A planet is needed, ")
      printerror("if you don't have a " + (buildmap) + ".o5m O5M-File! ")
      printerror("Please download one with 'planet_up'.")
      printerror("")
      printerror("The first planet will be updated by 'planet_up', ")
      printerror("but the extracted mapdata can be updated with ")
      printerror("'pygmap3', this function ist enabled by default ")
      printerror("disable it with 'keep_data'. ")
      printerror("'HINT: 'keep_data' is a FlipFlop. ")
      quit()

    
    mapdata.create_o5m()

  """
  update mapdata

  """

  mapdata.update_o5m()

else:
  printwarning("keep_data switched on!")
  ExitCode = os.path.exists(buildmap_o5m)
  if ExitCode == False:
    printerror("no mapdata not found, " +
	      "please run 'keep_data' to remove the lockfile!")
    quit()
    
os.chdir(WORK_DIR)
config.read('pygmap3.cfg')

description = (buildmap) + "_" + (config.get((buildmap), 'buildday'))
printinfo(description)


"""
split rawdata

"""

os.chdir(WORK_DIR)
def remove_old_tiles():
  path = 'tiles'
  for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
      try:
        os.remove(os.path.join(path, file))
      except:
        print('Could not delete', file, 'in', path)
ExitCode = os.path.exists((WORK_DIR) + "no_split.lck")
if ExitCode == False:
  remove_old_tiles()

  os.chdir(WORK_DIR)

  splitter.split()

elif ExitCode == True:
  printwarning("no_split switched on!")
  ExitCode = os.path.exists((WORK_DIR) +
             "tiles/" + (buildmap) + "_split.ready")
  if ExitCode == False:
    printwarning("have to split once again!")
    remove_old_tiles()

    os.chdir(WORK_DIR)

    splitter.split()



"""
render the map-images

"""

mkgmap.render()

os.chdir(WORK_DIR)


"""
create the contourlines

"""


if (config.get('contourlines', 'build')) == "yes":
  contourlines.create_cont()

os.chdir(WORK_DIR)

os.remove((WORK_DIR) + "pygmap3.lck")

printinfo("Habe fertig!")

quit()


"""

## Changelog

v0.9.49 - update only the needed mapdata with osmupdate
          move planet to $WORK_DIR/o5m

v0.9.48 - add 7z as output for the images
        - mapid for DACH and germany

v0.9.47 - navmaps.eu is down, use navmaps.org manually

v0.9.46 - boundaries and precomp_sea from navmaps.eu

v0.9.45 - more options to config

v0.9.44 - first steps for configparser

v0.9.43 - download from geofabrik removed

v0.9.42 - create contourlines if needed

v0.9.41 - dir for splitter-output

v0.9.40 - more python, removed 'test -[f|d]'

v0.9.38 - mkgmap.org, sitestructure is changed

v0.9.37 - use *.o5m as input for splitter

v0.9.36 - simplify workprocess

v0.9.35 - some changes in workprocess
          some changes at mkgmap-options


"""

