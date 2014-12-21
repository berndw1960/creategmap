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
__version__ = "0.0.2"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2012 Bernd Weigelt"
__license__ = "AGPLv3"
__maintainer__ = "Bernd Weigelt"
__email__ = "weigelt.bernd@web.de"
__status__ = "RC"

import sys
import os

WORK_DIR = (os.environ['HOME'] + "/map_build/")

def printinfo(msg):
  print(("II: " + msg))

def printwarning(msg):
  print(("WW: " + msg))

def printerror(msg):
  print(("EE: " + msg))


def checkprg(programmtofind, solutionhint):
  """
    test if an executable can be found by
    following $PATH
    raise message if fails and returns 1
    on success return 0
    search follows $PATH
  """

  ExitCode = os.system("which " + programmtofind)

  if ExitCode == 0:
    printinfo(programmtofind + " found")
  else:
    printerror(programmtofind + " not found")
    print(solutionhint)
    quit()

def is_there(find, solutionhint):
  """
    test if a file or dir can be found at a predefined place
    raise message if fails and returns 1
    on success return 0
  """

  ExitCode = os.path.exists(find)

  if ExitCode == True:
     printinfo(find + " found")
  else:
    printerror(find + " not found")
    print(solutionhint)


hint = ("mkdir " + (WORK_DIR))
is_there((WORK_DIR), hint)

os.chdir(WORK_DIR)

for tool in ['osmconvert', 'osmupdate']:
  hint = (tool) + " missed, please use mk_osmtools to build it from sources"
  checkprg((tool), hint)

ExitCode = os.path.exists("planet.o5m")
if ExitCode == True:
  printerror("please move planet.o5m to " +(WORK_DIR) + "o5m/")
  quit()

hint = ("No Planet-File found! ")
is_there("o5m/planet.o5m", hint)


ExitCode = os.path.exists("o5m/planet.o5m")
if ExitCode == False:
  os.chdir("o5m/")
  printinfo("Download started. Size ~30 Gigabytes... please wait! ")
  os.system("wget http://ftp5.gwdg.de/pub/misc/openstreetmap/planet.openstreetmap.org/pbf/planet-latest.osm.pbf")
  os.system("osmconvert planet-latest.osm.pbf -o=planet.o5m")
  os.remove("planet-latest.osm.pbf")
  os.chdir(WORK_DIR)

"""
check for pygmap3.cfg
"""

import configparser

config = configparser.ConfigParser()

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

ExitCode = os.path.exists("pygmap3.cfg")
if ExitCode == False:
  import default_config
  default_config.create()

config.read('pygmap3.cfg')

if ('planet' in config) == False:
  config.add_section('planet')
  write_config()

"""
set date for info

"""
import datetime

today = datetime.datetime.now()
DATE = today.strftime('%Y%m%d_%H00')

config.set('planet', 'buildday', (DATE))
write_config()


os.system("osmupdate -v --daily --hourly --keep-tempfiles o5m/planet.o5m o5m/planet_new.o5m")

os.chdir("o5m/")

ExitCode = os.path.exists("planet_new.o5m")
if ExitCode == True:
  os.rename("planet.o5m", "planet_temp.o5m")
  os.rename("planet_new.o5m", "planet.o5m")
  ExitCode = os.path.exists("planet.o5m")
  if ExitCode == True:
    os.remove("planet_temp.o5m")

os.chdir(WORK_DIR)

printinfo("Habe fertig!")
quit()

