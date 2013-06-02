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
__version__ = "0.9.47"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2012 Bernd Weigelt"
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
import fetch
import get_tools
import splitter
import mkgmap
import contourlines
import navmap

"""
argparse

"""

parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\

            To build maps for Garmin PNA

            Basemap (embedded)
            Bikemap (embedded)
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

hint = "Install: 7z to extract mkgmap's stylefiles"
checkprg("7z", hint)

ExitCode = os.path.exists(WORK_DIR)
if ExitCode == False:
  printerror("Please create" + (WORK_DIR))
  quit()

os.chdir(WORK_DIR)

ExitCode = os.path.exists("pygmap3.lck")
if ExitCode == True:
  printerror("Is there another instance of pygmap3.py running?")

datei = open((WORK_DIR) + "pygmap3.lck", "w")
datei.close()

hint = ("No Planet-File found! ")
is_there("planet.o5m", hint)

ExitCode = os.path.exists("fixme_buglayer.conf")
if ExitCode == True:
  printerror(" Please rename 'fixme_buglayer.conf' to 'fixme.conf'")
  quit()


"""
configparser

"""
def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

config = configparser.ConfigParser()
ExitCode = os.path.exists("pygmap3.cfg")
if ExitCode == False:
  config['DEFAULT'] = {}

  config['ramsize'] = {}
  config['ramsize'] = {'ramsize': '-Xmx3G',}

  config['mapid'] = {}
  config['mapid'] = {'mapid': '6389',}

  config['mapdata'] = {}
  config['mapdata'] = {'buildday': '2013_xx_yy'}

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
                   'family-name': 'RadReiseKarte',
                   'draw-priority': '12',
                   'mapid_ext': '3001',}

  config['rrk'] = {}
  config['rrk'] = {'family-id': '1',
                   'product-id': '1000',
                   'family-name': 'RadReiseKarte',
                   'draw-priority': '12',
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
  config['store_as'] = {'zip_img': 'no',}


elif ExitCode == True:
  config.read('pygmap3.cfg')

write_config()

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
buildday = config.get('mapdata', 'buildday')

description = ((buildmap) + "_" + (buildday))

config.set('runtime', 'description', (description))
write_config()

printinfo(description)


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

BUILD_O5M = ((WORK_DIR) + "o5m/" + (buildmap) + ".o5m")
ExitCode = os.path.exists("keep_data.lck")
if ExitCode == False:
  printinfo("keep_data switched off!")
  fetch.fetch()
else:
  printwarning("keep_data switched on!")
  ExitCode = os.path.exists(BUILD_O5M)
  if ExitCode == False:
    fetch.fetch()

"""
split rawdata

"""

os.chdir(WORK_DIR)

ExitCode = os.path.exists((WORK_DIR) + "no_split.lck")
if ExitCode == False:
  path = 'tiles'
  for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
      try:
        os.remove(os.path.join(path, file))
      except:
        print('Could not delete', file, 'in', path)

  os.chdir(WORK_DIR)

  splitter.split()

elif ExitCode == True:
  printwarning("no_split switched on!")
  ExitCode = os.path.exists((WORK_DIR) +
             "tiles/" + (buildmap) + "_split.ready")
  if ExitCode == False:
    printwarning("have to split once again!")
    path = 'tiles'
    for file in os.listdir(path):
      if os.path.isfile(os.path.join(path, file)):
        try:
          os.remove(os.path.join(path, file))
        except:
          print('Could not delete', file, 'in', path)

    os.chdir(WORK_DIR)

    splitter.split()

"""
make the dirs to store the images

"""

os.chdir(WORK_DIR)


zip_dir = ((WORK_DIR) + "gps_ready/zipped/" + (buildmap) + "/" + (buildday) + "/")
unzip_dir = ((WORK_DIR) + "gps_ready/unzipped/" + (buildmap) + "/" + (buildday) + "/")

cl_dir = ((WORK_DIR) + "contourlines/" + (buildmap) + "/")
cltemp_dir = ((WORK_DIR) + "contourlines/temp/")

for dir in [(zip_dir), (unzip_dir), (cltemp_dir)]:
  ExitCode = os.path.exists(dir)
  if ExitCode == True:
    path = (dir)
    for file in os.listdir(path):
      if os.path.isfile(os.path.join(path, file)):
        try:
          os.remove(os.path.join(path, file))
        except:
          print('Could not delete', file, 'in', path)

  elif ExitCode == False:
    os.makedirs(dir)

ExitCode = os.path.exists(cl_dir)
if ExitCode == False:
  os.makedirs(cl_dir)


"""
render the map-images

"""

mkgmap.render()

os.chdir(WORK_DIR)


"""
create the contourlines

"""

build = (config.get('contourlines', 'build'))
if build == "yes":
  contourlines.create_cont()

"""
copy *kml to zipp-dirs

"""

os.chdir(WORK_DIR)

ExitCode = os.path.exists("tiles/" + (buildmap) + ".kml")
if ExitCode == True:
  os.system("mv tiles/" + (buildmap) + ".kml " + (zip_dir))


"""
zipp the images and mv them to separate dirs

"""

zip_img = (config.get('store_as', 'zip_img'))
if zip_img == "yes":
  os.chdir(unzip_dir)
  os.system("for file in *.img; do zip $file.zip $file; done")
  os.system("mv *.zip " + (zip_dir))

os.chdir(WORK_DIR)

os.remove((WORK_DIR) + "pygmap3.lck")

printinfo("Habe fertig!")

quit()


"""

## Changelog
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

