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
__version__ = "0.9.37"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2012 Bernd Weigelt"
__credits__ = "Dschuwa"
__license__ = "AGPLv3"
__maintainer__ = "Bernd Weigelt"
__email__ = "weigelt.bernd@web.de"
__status__ = "RC"

""" 
  
  pygmap3.py, das script um ein gmapsupp.img für GARMIN-Navigationsgeräte
  zu erzeugen, z.B. Garmin eTrex Vista Hcx
    
  Work in progress, bitte beachten!
  Prinzipiell funktioniert es, aber wenn was kaputt geht, 
  lehnen wir jegliche Haftung ab.
  
  
  Folgende Software wird benutzt:
  
  mkgmap from 
  http://wiki.openstreetmap.org/wiki/Mkgmap
  
  splitter from
  http://www.mkgmap.org.uk/page/tile-splitter
  splitter.jar 
  
  gmaptool from
  http://www.anpo.republika.pl/download.html
  ~/bin/gmt.exe
  
  osmconvert and osmupdate
 
"""

import sys
import os
import http.client
import re
import tarfile
import datetime
import argparse
import random

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






"""
  argparse
  
"""

parser = argparse.ArgumentParser(
        prog='PROG', 
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\
        
            Zum Bauen diverser Karten für Garmin PNA
            Verfügbar aktuell:
            AIO-Basemap
            
            ############################################################
            # Work in progress, bitte beachten!                        #
            # Prinzipiell funktioniert es, aber wenn was kaputt geht,  #
            # lehnen wir jegliche Haftung ab                           #
            ############################################################
            
            
            
            Das Copyright der Styles liegt bei den jeweiligen Autoren!
            
            
            Als Basis können alle Dateien unter
            http://download.geofabrik.de/openstreetmap/
            verwendet werden.
            
            pygmap3 -b germany -c europe 
                      
            
            Oder mit lokalem Planet möglich...
            
            ...als BBOX:
            
            Benelux	--> -b benelux  
            Bonn	--> -b bonn
            
            ...per poly:            
            
            Eigene poly-Dateien können im Verzeichnis 'poly' im Arbeitsverzeichnis
            abgelegt werden. 
            Der Namen muss identisch zur Karte sein mit der Endung '.poly'
                          
            Hamburg     --> -b hamburg  
            Bayern      --> -b bayern
            Deutschland --> -b germany
            Europa	--> -b europe (nicht nutzbar wegen FAT, zu groß!)   
            
            Andere Einstellungen können bei Bedarf angepasst werden.
            
            RAMSIZE = "3000M" or "4G" (default)
            MAXNODES = "1600000" (default)
            MKGMAP_VERSION = use a defined mkgmap-version, 
                             for available versions
                             http://www.mkgmap.org.uk/snapshots/
            SPLITTER_VERSION = same as before for splitter    
            
        '''))

parser.add_argument('-c', '--continent', dest='continent', default='europe')
parser.add_argument('-b', '--buildmap', dest='build_map', default='dach')
parser.add_argument('-r', '--ramsize', dest='ramsize', default='3G')
parser.add_argument('-m', '--maxnodes', dest='maxnodes', default='1600000')
parser.add_argument('-mkv', '--mkgmap_version', dest='mkgmap_version', default=0)
parser.add_argument('-spv', '--splitter_version', dest='splitter_version', default='236')
parser.add_argument('-w', '--work_dir', dest='work_dir', default='map_build')
args = parser.parse_args()


CONTINENT = (args.continent)
BUILD_MAP = (args.build_map)
PREFIX = "-Xmx"
RAMSIZE = ((PREFIX) + (args.ramsize))
MAXNODES = (args.maxnodes)
MKGMAP_VERSION = (args.mkgmap_version)
SPLITTER_VERSION = (args.splitter_version)
WORK_DIR = (os.environ['HOME'] + "/"  + (args.work_dir) + "/")

# Der letzte Slash muss sein!!!


"""
  needed programs und dirs
  
"""

hint = ("mkdir " + (WORK_DIR))
checkdir((WORK_DIR), hint) 

os.chdir(WORK_DIR)

hint = " osmconvert missed, needed to cut data from the planet.o5m"
checkprg("osmconvert", hint)

hint = "get the bounds-*.zip from navmaps.eu and rename it to bounds.zip"
checkfile("bounds.zip", hint)


"""
  get splitter and mkgmap 
  
"""  
target = http.client.HTTPConnection("www.mkgmap.org.uk")

if SPLITTER_VERSION != 0:
  ExitCode = os.system("test -d splitter-r" + (SPLITTER_VERSION))
  if ExitCode != 0:
    os.system(("wget -N http://www.mkgmap.org.uk/snapshots/splitter-r") + 
	      (SPLITTER_VERSION) + (".tar.gz"))
    tar = tarfile.open((WORK_DIR) + "splitter-r" + 
                       (SPLITTER_VERSION) + (".tar.gz"))
    tar.extractall()
    tar.close()   
  
  splitter = ((WORK_DIR) + "splitter-r" + (SPLITTER_VERSION) + "/splitter.jar")
  
else:    
  target.request("GET", "/splitter/index.html")
  htmlcontent =  target.getresponse()
  print(htmlcontent.status, htmlcontent.reason)
  data = htmlcontent.read()
  data = data.decode('utf8')
  pattern = re.compile('splitter-r\d{3}')
  splitter_rev = sorted(pattern.findall(data), reverse=True)[1]
  target.close()
  os.system(("wget -N http://www.mkgmap.org.uk/splitter/") + 
            (splitter_rev) + (".tar.gz"))
  tar = tarfile.open((WORK_DIR) + (splitter_rev) + (".tar.gz"))
  tar.extractall()
  tar.close()    
    
  splitter = ((WORK_DIR) + (splitter_rev) + "/splitter.jar")

if MKGMAP_VERSION != 0:
  ExitCode = os.system("test -d mkgmap-r" + (MKGMAP_VERSION))
  if ExitCode != 0:
    os.system(("wget -N http://www.mkgmap.org.uk/snapshots/mkgmap-r") + 
              (MKGMAP_VERSION) + (".tar.gz"))
    tar = tarfile.open((WORK_DIR) + "mkgmap-r" + 
                       (MKGMAP_VERSION) + (".tar.gz"))
    tar.extractall()
    tar.close()
  
  mkgmap = (WORK_DIR) + "mkgmap-r" + (MKGMAP_VERSION) + "/mkgmap.jar"
  

else:
  target.request("GET", "/snapshots/index.html")
  htmlcontent =  target.getresponse()
  print(htmlcontent.status, htmlcontent.reason)
  data = htmlcontent.read()
  data = data.decode('utf8')
  pattern = re.compile('mkgmap-r\d{4}')
  mkgmap_rev = sorted(pattern.findall(data), reverse=True)[1]
  target.close()
  os.system(("wget -N http://www.mkgmap.org.uk/snapshots/") + 
            (mkgmap_rev) + (".tar.gz"))
  tar = tarfile.open((WORK_DIR) + (mkgmap_rev) + (".tar.gz"))
  tar.extractall()
  tar.close()

  mkgmap = (WORK_DIR) + (mkgmap_rev) + "/mkgmap.jar"

target.close()


"""
  cut data from planet-file or get the raw map-extracts from the geofabrik 
  
"""  
def fetch():
  ExitCode = os.system("test -f planet.o5m")
  if ExitCode == 0:
    ExitCode = os.system("test -f poly/" + (BUILD_MAP) + ".poly")
    if ExitCode == 0:                     
      os.system("osmconvert planet.o5m " +
                "--complete-ways --complex-ways " +
                " -B=poly/" + (BUILD_MAP) + ".poly " +
                " -o=" + (BUILD_MAP) + ".o5m")
      
    elif (BUILD_MAP) == "dach":
      os.system("osmconvert planet.o5m " +
                "--complete-ways --complex-ways " +
                " -b=5,45,18,56 " +
                " -o=" + (BUILD_MAP) + ".o5m")
  
    elif (BUILD_MAP) == "benelux":  
      os.system("osmconvert planet.o5m " +
                "--complete-ways --complex-ways " +
                " -b=1,49,8,54 " +
                " -o=" + (BUILD_MAP) + ".o5m")    
      
    elif (BUILD_MAP) == "bonn":  
      os.system("osmconvert planet.o5m " + 
                "--complete-ways --complex-ways " +
                " -b=6.1,49.7,8.1,51.7 " +
                " -o=" + (BUILD_MAP) + ".o5m")    
      
    elif (BUILD_MAP) == "th_sn":  
      os.system("osmconvert planet.o5m " + 
                "--complete-ways --complex-ways " +
                " -b=9.93,50.4,14.9,51.53 " +
                " -o=" + (BUILD_MAP) + ".o5m") 
      
    elif (BUILD_MAP) == "voralpen":  
      os.system("osmconvert planet.o5m " + 
                "--complete-ways --complex-ways " +
                " -b=9,47,14,49 " +
                " -o=" + (BUILD_MAP) + ".o5m")    
      
    else:
      printerror("no poly or BBOX found... exit")
      quit()

  else:  
     os.system("wget -N http://download.geofabrik.de/openstreetmap/" + 
              (CONTINENT) + "/" + (BUILD_MAP) + ".osm.pbf")
     os.system("osmconvert " + 
	      (BUILD_MAP) + ".osm.pbf  --out-o5m > " + (BUILD_MAP) + ".o5m")  


"""
is there a keep_pbf.lck, then use the old data

"""
  
ExitCode = os.system("test -f keep_pbf.lck")
if ExitCode != 0:
  printinfo("keep_pbf switched off!")
  fetch()
else:
  ExitCode = os.system("test -f " +  (WORK_DIR) + (BUILD_MAP) + ".o5m")
  if ExitCode != 0:
    fetch()
  
"""
  create (WORK_DIR) for splitter
  
"""  
 
ExitCode = os.system("test -d tiles")

if ExitCode == 0:
  os.chdir("tiles")
  os.system("rm -Rf *")
  os.chdir(WORK_DIR)
	  
else: 
    os.mkdir("tiles")

"""
  create dir for areas
  
"""  
 
ExitCode = os.system("test -d areas")

if ExitCode != 0:
  os.mkdir("areas")
    
"""
  random mapid, just fun, not really needed
  
"""

MAPID = random.randint(6301, 6399)



"""
  split rawdata
  
"""

ExitCode = os.system("test -f areas/" + (BUILD_MAP) + "_areas.list")
if ExitCode == 0:
  os.chdir("tiles")
  os.system("java -ea " + (RAMSIZE) + 
	   " -jar " + (splitter) + 
           " --split-file=" + (WORK_DIR) + "areas/" + (BUILD_MAP) + "_areas.list " +
           " --geonames-file=" + (WORK_DIR) + "cities15000.txt " +
           " --mapid=" + str(MAPID) + "0001 " +
           " --keep-complete " +
           " --write-kml=" +  (BUILD_MAP) + ".kml "
           " --max-areas=1024 " +
           " --max-nodes=" + (MAXNODES) + 
           " --overlap=0 " +
           (WORK_DIR) + (BUILD_MAP) + ".o5m")
else:
  os.chdir("tiles")
  os.system("java -ea " + (RAMSIZE) + 
           " -jar " + (splitter) +
           " --geonames-file=" + (WORK_DIR) + "cities15000.txt " +
           " --mapid=" + str(MAPID) + "0001 " +
           " --keep-complete " +
           " --write-kml=" +  (BUILD_MAP) + ".kml "
           " --max-areas=1024 " +
           " --max-nodes=" + (MAXNODES) + 
           " --overlap=0 " +
           (WORK_DIR) + (BUILD_MAP) + ".o5m")
  os.system("cp areas.list " + (WORK_DIR) + "areas/" + (BUILD_MAP) + "_areas.list")
  
os.chdir(WORK_DIR)

"""
  create mapdirs
  
"""

for dir in ['gfixme', 'gbasemap', 'gboundary', 'gps_ready']:
  ExitCode = os.system("test -d " + (dir))
  if ExitCode != 0:
    os.mkdir(dir)

"""
  add your own styles in mystyles, as an example rrk_style and rrk_typ 
    
"""

def style():
  os.chdir(WORK_DIR)
  ExitCode = os.system("test -d " + (WORK_DIR) + "mystyles/" + 
                         (layer) + "_style")
  global mapstyle
  if ExitCode == 0:
    mapstyle = "mystyles"
  else:
    printerror("Where are the styles? ")
    quit()
  
def cleanup():  
  os.chdir((WORK_DIR) + "/g" + (layer))
  print((layer) + "-layer build with " + (mapstyle))
  os.system("rm -Rf * ")
  
""" 
 create Bugs- and FIXME-Layer 
 
"""

layer = "boundary"
style()
cleanup()
os.system("java -ea " + (RAMSIZE) + 
#          " -Dlog.config=" + (WORK_DIR) + "log.conf " +
          " -jar " + (mkgmap) + 
          " -c " + (WORK_DIR) + "fixme_buglayer.conf " +
          " --style-file=" + (WORK_DIR) + (mapstyle) + "/boundary_style " +
          " --description='" + (BUILD_MAP) + " OSM-boundary' " +
          " --family-id=6 " +
          " --product-id=30 " +
          " --series-name=OSM-boundary " +
          " --family-name=OSM-boundary " + 
          " --mapname=" + str(MAPID) + "5001  " +
          " --draw-priority=14 " + 
          " -c " + (WORK_DIR) + "tiles/template.args " +
          (WORK_DIR) + (mapstyle) + "/boundary_typ.txt")

layer = "fixme"
style()
cleanup()
os.system("java -ea " + (RAMSIZE) + 
#          " -Dlog.config=" + (WORK_DIR) + "log.conf " +
          " -jar " + (mkgmap) +
          " -c " + (WORK_DIR) + "fixme_buglayer.conf " + 
          " --style-file=" + (WORK_DIR) + (mapstyle) + "/fixme_style " +
          " --description='" + (BUILD_MAP) + " OSM-fixme' " +
          " --family-id=3 " +
          " --product-id=33 " + 
          " --series-name=OSM-fixme " +
          " --family-name=OSM-fixme " + 
          " --mapname=" + str(MAPID) + "6001 " + 
          " --draw-priority=16 " + 
          " -c " + (WORK_DIR) + "tiles/template.args " + 
          (WORK_DIR) + (mapstyle) + "/fixme_typ.txt")
  


"""
  some defs
  
"""  
def basemap():
  global layer
  layer = "basemap"
  style()
  cleanup()
  os.system("java -ea " + (RAMSIZE) + 
            " -Dlog.config=" + (WORK_DIR) + "log.conf " +
            " -jar " + (mkgmap) + 
            " -c " + (WORK_DIR) + "map.conf " +
            " --style-file=" + (WORK_DIR) + (mapstyle) + "/basemap_style " + 
            " --description='" + (BUILD_MAP) + " AIO-basemap' " +
            " --bounds=" + (WORK_DIR) + "bounds.zip " +
            " --family-id=4 --product-id=45 " + 
            " --series-name=AIO-basemap " +
            " --family-name=AIO-basemap " + 
            " --mapname=" + str(MAPID) + "2001 " + 
            " --draw-priority=10 " + 
            " -c " + (WORK_DIR) + "tiles/template.args " + 
            (WORK_DIR) + (mapstyle) + "/basemap_typ.txt")
  os.chdir(WORK_DIR)
  

"""
  one dircectory per day 
"""  





def mk_store():

  os.chdir(WORK_DIR)

  for dir in [(dir1), (dir2), (dir3)]:
    ExitCode = os.system("test -d " +  (dir))
    if ExitCode == 0:
      os.system("rm -Rf " + (dir)) 
      os.makedirs(dir)
    elif ExitCode != 0:
      os.makedirs(dir)



"""
  rename the images

"""  

def copy_parts():
  
  os.chdir(WORK_DIR)
  
  for dir in ['gfixme', 'gboundary', 'gbasemap']:
    os.system("cp " + (dir) + "/gmapsupp.img "  + 
             (WORK_DIR) + "gps_ready/unzipped/" + (BUILD_MAP) + 
             "/" + (day) + 
             "/"  + (BUILD_MAP) + "_" + (dir) + "_gmapsupp.img")

  ExitCode = os.system("test -f hoehenlinien/" + (BUILD_MAP) + "/gmapsupp.img")
  if ExitCode == 0:
    os.system("cp hoehenlinien/" + (BUILD_MAP) + "/gmapsupp.img " + 
             (WORK_DIR) + "gps_ready/unzipped/" + (BUILD_MAP) + 
             "/" + (day) + 
             "/"  + (BUILD_MAP) + "_gcontourlines_gmapsupp.img")

  ExitCode = os.system("test -f " + (WORK_DIR) + "tiles/" + (BUILD_MAP) + ".kml ")
  if ExitCode == 0: 
    os.system("mv " + (WORK_DIR) + "tiles/" + (BUILD_MAP) + ".kml " + (WORK_DIR) + (dir1))
  
  ExitCode = os.system("test -f " + (WORK_DIR) + "gbasemap/mkgmap.log.0 ")
  if ExitCode == 0:
    os.system("mv " + (WORK_DIR) + "gbasemap/mkgmap.log.* " + (WORK_DIR) + (dir3))
    
    
"""
  zipp the images and mv them to separate dirs

"""

def zip_file():
  
  os.chdir(WORK_DIR)
  
  os.chdir(dir2)
  os.system("for file in *.img; do zip $file.zip $file; done")
  os.system("mv *.zip " + (WORK_DIR) + (dir1))



basemap()


today = datetime.datetime.now()
day = today.strftime('%Y_%m_%d') 
dir1 = ("gps_ready/" + (BUILD_MAP) + "/" + (day))
dir2 = ("gps_ready/unzipped/" + (BUILD_MAP) + "/" + (day))
dir3 = ("log/" + (BUILD_MAP) + "/" + (day))

mk_store()  
copy_parts()
zip_file()


printinfo("Habe fertig!")

""" 

## Changelog:

v0.9.37 - use *.o5m as input for splitter

v0.9.36 - simplify workprocess

v0.9.35 - some changes in workprocess
          some changes at mkgmap-options

v0.9.34 - dach.poly added
          keep areas.list for next runs
          remove rrk-code
          
v0.9.33 - TYP changed to TXT

v0.9.32 - Geofabrik path changed

v0.9.30 - use a planetfile if possible
	  look at the OSM-Wiki for infos about osmconvert and osmupdate

v0.9.24 - RadReiseKarte added, OSB removed

v0.9.22 - addr-Layer removed

v0.9.21 - predefined bundles of maps like DACH or Benelux

v0.9.20 - removed velomap-code 
	  use 7z for styles
	  removed git-code
	  some cleanups

v0.9.12 - options to change mapid 

v0.9.10	- offline-mode for splitter and mkgmap

v0.9.9	- defined mkgmap-version

v0.9.8	- added bounds-support

v0.9.7	- removed use of osm.bz2 and osm.gz, 
          use osm.pbf as new default by splitter, 
	  cleanups and comments

v0.9.6	- added function to set another continent

v0,9.5	- first version for Python 3.2.x 
	- commandline-otions added with argparse

v0.9.2	- addr- and boundary-layer added

v0.9.1	- zip-function added

## 2011-05-01 Projectstatus changed to RC


v0.8.0	- AIO-basemap as additional maptype

## 2011-02-14 Projectstatus changed to BETA

v0.6.7	- change WORK_DIR to map_build

v0.6.6	- better map-description, if more then one map is used on the GPS-device


v0.6.1	- first working version with python3, but there are a lot of things to do,
	  next is make it use startoptions and the pygmap.conf to remember these options
	  there are many systemcalls, which only work on Linux, they must be changed
	  removed many comments and code from the bash, because they make it unreadable

v0.6.0 	- Beginn der Umstellung auf python, aktuell noch nicht benutzbar

"""
