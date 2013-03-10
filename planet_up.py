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
import datetime
import configparser

# DEFs =============================================================================

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
    
# defaults =============================================================================

work_dir = (os.environ['HOME'] + "/map_build/") 

hint = ("mkdir " + (work_dir))
is_there((work_dir), hint) 

os.chdir(work_dir)

hint = "osmupdate missed, needed to update the planet.o5m"
checkprg("osmupdate", hint)

hint = ("No Planet-File found! ")
is_there("planet.o5m", hint)


    

"""
set date for info in PNA

"""

today = datetime.datetime.now()
DATE = today.strftime('%Y_%m_%d')

config = configparser.ConfigParser()
config.read('pygmap3.cfg')
config.set('mapdata', 'buildday', (DATE))
with open('pygmap3.cfg', 'w') as configfile:
  config.write(configfile)


ExitCode = os.path.exists("planet.o5m")
if ExitCode == False:
  printinfo("Download started. Size ~17+ Gigabytes... please wait! ")
  os.system("wget http://ftp5.gwdg.de/pub/misc/openstreetmap/planet.openstreetmap.org/pbf/planet-latest.osm.pbf")
  os.system("osmconvert planet-latest.osm.pbf -o=planet.o5m")
  os.remove("planet-latest.osm.pbf")
 
os.system("osmupdate -v --daily --hourly planet.o5m planet_new.o5m")

ExitCode = os.path.exists("planet_new.o5m")
if ExitCode == True:
  os.rename("planet.o5m", "planet_temp.o5m")
  os.rename("planet_new.o5m", "planet.o5m")
  ExitCode = os.path.exists("planet.o5m")
  if ExitCode == True:      
    os.remove("planet_temp.o5m") 
  
printinfo("Habe fertig!")
quit()

