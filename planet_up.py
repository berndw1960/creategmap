#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "0.0.1"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2012, The OSM-TroLUG-Project"
__license__ = "GPL"
__maintainer__ = "Bernd Weigelt"
__email__ = "weigelt.bernd@web.de"
__status__ = "Alpha" 

import sys
import os
import datetime


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

  return ExitCode

def checkfile(filetofind, solutionhint):
  """
    test if a file can be found at a predefined place
    raise message if fails and returns 1
    on success return 0
  """

  ExitCode = os.system("test -f " + filetofind)
    
  if ExitCode == 0:
     printinfo(filetofind + " found")
  else:
    printerror(filetofind + " not found")
    print(solutionhint)

  return ExitCode

def checkdir(dirtofind, solutionhint):
  """
    test if a dir can be found  at a predefined place
    raise message if fails and returns 1
    on success return 0
  """

  ExitCode = os.system("test -d " + dirtofind)
    
  if ExitCode == 0:
    printinfo(dirtofind + " found")
  else:
    printerror(dirtofind + " not found")
    print(solutionhint)

# defaults =============================================================================

work_dir = (os.environ['HOME'] + "/share/osm/map_build/") 
# Der letzte Slash muss sein!!!


hint = ("mkdir " + (work_dir))
checkdir((work_dir), hint) 

os.chdir(work_dir)

hint = " osmupdate missed, needed to update the planet.osm.pbf"
checkprg("osmupdate", hint)

hint = (" No Planet-File found, it will be downloaded. Size ~15+ Gigabytes ")
checkfile("planet.osm.pbf", hint)


today = datetime.datetime.now()
day = today.strftime('%Y_%m_%d')

ExitCode = os.system("test -f planet.osm.pbf")
if ExitCode == 0:
  os.system("osmupdate -v --daily \
	     --planet-url=http://planet.openstreetmap.org/redaction-period/ \
	     planet.osm.pbf planet_new.osm.pbf") 

  ExitCode = os.system("test -f planet_new.osm.pbf")
  if ExitCode == 0:
    os.system("mv planet.osm.pbf planet-" + (day) + ".osm.pbf && \
               mv planet_new.osm.pbf planet.osm.pbf")
  else:
    printinfo("no new planet_file found... exit")
    (quit)

else:
  os.system("wget -N http://ftp5.gwdg.de/pub/misc/openstreetmap/planet.openstreetmap.org/pbf/planet-latest.osm.pbf \
            -o planet.osm.pbf")

printinfo("Habe fertig!")
(quit)

