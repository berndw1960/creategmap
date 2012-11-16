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
__version__ = "0.0.1"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2012 Bernd Weigelt"
__license__ = "AGPLv3"
__maintainer__ = "Bernd Weigelt"
__email__ = "weigelt.bernd@web.de"
__status__ = "RC" 

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
    quit()
 

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
    quit()
  

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
    quit()


# defaults =============================================================================

work_dir = (os.environ['HOME'] + "/map_build/") 
# Der letzte Slash muss sein!!!

hint = ("mkdir " + (work_dir))
checkdir((work_dir), hint) 

os.chdir(work_dir)

hint = " osmupdate missed, needed to update the planet.o5m"
checkprg("osmupdate", hint)

hint = (" No Planet-File found, download started. Size ~17+ Gigabytes ")
checkfile("planet.o5m", hint)


today = datetime.datetime.now()
day = today.strftime('%Y_%m_%d')

def update():
  os.system("osmupdate -v --daily --hourly \
	     planet.o5m planet_new.o5m")

ExitCode = os.system("test -f planet.o5m")
if ExitCode == 0:
  update() 
 
  ExitCode = os.system("test -f planet_new.o5m")
  if ExitCode == 0:
    os.system("mv planet.o5m planet-" + (day) + ".o5m && \
               mv planet_new.o5m planet.o5m")
  else:
    printerror("no new planet_file found... exit")
    quit()

else:
  os.system("wget \
    http://ftp5.gwdg.de/pub/misc/openstreetmap/planet.openstreetmap.org/pbf/planet-latest.osm.pbf")
  os.system("osmconvert planet-latest.osm.pbf -o=planet.o5m")
  update()
  
  
printinfo("Habe fertig!")
quit()

