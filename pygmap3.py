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
__version__ = "0.9.41"
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
    

"""
  add your own styles in mystyles
    
"""

def style():
  ExitCode = os.path.exists("mystyles/" + (layer) + "_style")
  global mapstyle
  if ExitCode == True:
    mapstyle = "mystyles"
  else:
    ExitCode = os.path.exists("aiostyles")
    if ExitCode == False:
      os.system("wget -N http://dev.openstreetmap.de/aio/aiostyles.7z")
      os.system("7z x aiostyles.7z -oaiostyles")
    mapstyle = "aiostyles"
    
  ExitCode = os.path.exists((mapstyle) + "/" + (layer) + "_typ.txt") 
  if ExitCode == False:
    printerror(" Please convert " +
        (WORK_DIR) + (mapstyle) + "/" + (layer) + ".TYP to " + (layer) + "_typ.txt!")
    quit()  

"""
  remove old files
 
"""

def cleanup():
  for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
      try:
        os.remove(os.path.join(path, file))
      except:
         print('Could not delete', file, 'in', path)
         
   



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
            The AIO-Style is PD
            
            
            Als Basis können alle Dateien unter
            http://download.geofabrik.de/openstreetmap/
            verwendet werden.
            
            pygmap3 -b germany -c europe 
                      
            
            Oder mit lokalem Planet möglich...

            ...per poly:            
            
            Eigene poly-Dateien können im Verzeichnis 'poly' im Arbeitsverzeichnis
            abgelegt werden. 
            Der Namen muss identisch zur Karte sein mit der Endung '.poly'
                          
            Hamburg     --> -b hamburg  
            Bayern      --> -b bayern
            Deutschland --> -b germany
            Europa	--> -b europe (nicht nutzbar wegen FAT, zu groß!)   
                                    
            Andere Einstellungen können bei Bedarf angepasst werden.
            
            RAMSIZE = "3000M" or "3G" (default)
            MAXNODES = "1600000" (default)
            MKGMAP_VERSION = use a defined mkgmap-version, 
                             for available versions
                             http://www.mkgmap.org.uk/download/mkgmap
            SPLITTER_VERSION = same as before for splitter    
            
        '''))

parser.add_argument('-c', '--continent', dest='continent', default='europe')
parser.add_argument('-b', '--buildmap', dest='build_map', default='dach')
parser.add_argument('-r', '--ramsize', dest='ramsize', default='3G')
parser.add_argument('-m', '--maxnodes', dest='maxnodes', default='1200000')
parser.add_argument('-mkv', '--mkgmap_version', dest='mkgmap_version', default=0)
parser.add_argument('-spv', '--splitter_version', dest='splitter_version', default=0)
parser.add_argument('-w', '--work_dir', dest='work_dir', default='map_build')
args = parser.parse_args()


CONTINENT = (args.continent)
BUILD_MAP = (args.build_map)
BUILD_FROM_O5M = ("o5m/" +(args.build_map) + ".o5m")
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

hint = "osmconvert missed, needed to cut data from the planet.o5m"
checkprg("osmconvert", hint)

hint = "Install: 7z to extract mkgmap's stylefiles"
checkprg("7z", hint)

os.chdir(WORK_DIR)

hint = "get the bounds-*.zip from navmaps.eu and rename it to bounds.zip"
is_there("bounds.zip", hint)


"""
  dirs generate or wiped
  
"""

for dir in ['gfixme', 'gbasemap', 'tiles']:
  ExitCode = os.path.exists(dir)
  if ExitCode == False:
    os.mkdir(dir)
  else:
    path = (dir)
    cleanup()

"""
  create dir for areas. poly and splitter-output
  
"""  
for dir in ['o5m', 'areas', 'poly', 'hoehenlinien']: 
  ExitCode = os.path.exists(dir)
  if ExitCode == False:
   os.mkdir(dir)


"""
  get splitter and mkgmap 
  
"""  
target = http.client.HTTPConnection("www.mkgmap.org.uk")

if SPLITTER_VERSION != 0:
  ExitCode = os.path.exists("splitter-r" + (SPLITTER_VERSION))
  if ExitCode == False:
    os.system(("wget -N http://www.mkgmap.org.uk/download/splitter-r") + 
	      (SPLITTER_VERSION) + (".tar.gz"))
    tar = tarfile.open("splitter-r" + (SPLITTER_VERSION) + (".tar.gz"))
    tar.extractall()
    tar.close()   
  
  splitter = ((WORK_DIR) + "splitter-r" + (SPLITTER_VERSION) + "/splitter.jar")
  
else:    
  target.request("GET", "/download/splitter.html")
  htmlcontent =  target.getresponse()
  print(htmlcontent.status, htmlcontent.reason)
  data = htmlcontent.read()
  data = data.decode('utf8')
  pattern = re.compile('splitter-r\d{3}')
  splitter_rev = sorted(pattern.findall(data), reverse=True)[1]
  target.close()
  os.system(("wget -N http://www.mkgmap.org.uk/download/") + 
            (splitter_rev) + (".tar.gz"))
  tar = tarfile.open((splitter_rev) + (".tar.gz"))
  tar.extractall()
  tar.close()    
    
  splitter = ((WORK_DIR) + (splitter_rev) + "/splitter.jar")

if MKGMAP_VERSION != 0:
  ExitCode = os.path.exists("mkgmap-r" + (MKGMAP_VERSION))
  if ExitCode == False:
    os.system(("wget -N http://www.mkgmap.org.uk/download/mkgmap-r") + 
              (MKGMAP_VERSION) + (".tar.gz"))
    tar = tarfile.open("mkgmap-r" + (MKGMAP_VERSION) + (".tar.gz"))
    tar.extractall()
    tar.close()
  
  mkgmap = (WORK_DIR) + "mkgmap-r" + (MKGMAP_VERSION) + "/mkgmap.jar"
  

else:
  target.request("GET", "/download/mkgmap.html")
  htmlcontent =  target.getresponse()
  print(htmlcontent.status, htmlcontent.reason)
  data = htmlcontent.read()
  data = data.decode('utf8')
  pattern = re.compile('mkgmap-r\d{4}')
  mkgmap_rev = sorted(pattern.findall(data), reverse=True)[1]
  target.close()
  os.system(("wget -N http://www.mkgmap.org.uk/download/") + 
            (mkgmap_rev) + (".tar.gz"))
  tar = tarfile.open((mkgmap_rev) + (".tar.gz"))
  tar.extractall()
  tar.close()

  mkgmap = (WORK_DIR) + (mkgmap_rev) + "/mkgmap.jar"

target.close()


"""
  get the geonames for splitter
  
"""

ExitCode = os.path.exists("cities15000.zip")
if ExitCode == False:
  os.system("wget http://download.geonames.org/export/dump/cities15000.zip")

"""
  date 
"""  

today = datetime.datetime.now()
DAY = today.strftime('%Y_%m_%d')
BUILD_DAY = ((BUILD_MAP) + "/" + (DAY))


"""
  cut data from planet-file or get the raw map-extracts from the geofabrik 
  
""" 

def fetch():
  ExitCode = os.path.exists("planet.o5m")
  if ExitCode == True:
    ExitCode = os.path.exists("poly/" + (BUILD_MAP) + ".poly")
    if ExitCode == True:
      printinfo("I'm now extracting " + (BUILD_MAP) + ".o5m from Planet")      
      os.system("osmconvert planet.o5m " +
                "--complete-ways --complex-ways " +
                " -B=poly/" + (BUILD_MAP) + ".poly " +
                " -o=" + (BUILD_FROM_O5M))
    else:
      printerror("no poly found... exit")
      quit()

  else:  
     os.system("wget -N http://download.geofabrik.de/openstreetmap/" + 
              (CONTINENT) + "/" + (BUILD_MAP) + ".osm.pbf")
     os.system("osmconvert " + 
	      (BUILD_MAP) + ".osm.pbf  --out-o5m > " + (BUILD_FROM_O5M))  
         
       

"""
is there a keep_pbf.lck, then use the old data

"""
  
ExitCode = os.path.exists("keep_pbf.lck")
if ExitCode == False:
  printinfo("keep_pbf switched off!")
  fetch()
else:
  printwarning("keep_pbf switched on!")
  ExitCode = os.path.exists(BUILD_FROM_O5M)
  if ExitCode == False:
    fetch()

    
"""
  random mapid, just fun, not really needed
  
"""

MAPID = random.randint(6301, 6399)


"""
  split rawdata
  
"""
java_opts = ("java -ea " + (RAMSIZE) + " -jar " + (splitter))
splitter_opts = (" --geonames-file=" + (WORK_DIR) + "cities15000.zip " +
		 " --mapid=" + str(MAPID) + "0001 " +
		 " --output=o5m " +
		 " --keep-complete " +
		 " --write-kml=" + (BUILD_MAP) + ".kml "
		 " --max-nodes=" + (MAXNODES) + 
		 " --overlap=0 ")
areas_list = (" --split-file=" + (WORK_DIR) + "areas/" + (BUILD_MAP) + "_areas.list ")
map_data = ((WORK_DIR) + (BUILD_FROM_O5M))

ExitCode = os.path.exists("areas/" + (BUILD_MAP) + "_areas.list")
if ExitCode == True:
  os.chdir("tiles")
  os.system((java_opts) + (splitter_opts) + (areas_list) + (map_data))
else:
  os.chdir("tiles")
  os.system((java_opts) + (splitter_opts) + (map_data))
  os.system("cp areas.list ../areas/" + (BUILD_MAP) + "_areas.list")
  
os.chdir(WORK_DIR)

""" 
 create the layers 
 
"""

os.chdir(WORK_DIR)
layer = "basemap"

style()

os.chdir("g" + (layer))
printinfo("entered " + os.getcwd())


printinfo((layer) + "-layer build with " + (mapstyle))
os.system("java -ea " + (RAMSIZE) + 
          " -Dlog.config=" + (WORK_DIR) + "log.conf " +
          " -jar " + (mkgmap) + 
          " -c " + (WORK_DIR) + "map.conf " +
          " --style-file=" + (WORK_DIR) + (mapstyle) + "/basemap_style " +
          " --bounds=" + (WORK_DIR) + "bounds.zip " +
          " --mapname=" + str(MAPID) + "1001 " +
          " --family-id=4  " +
          " --product-id=45 " + 
          " --description=" + (BUILD_DAY) +
          " --family-name=AIO-Basemap " +
          " --draw-priority=10 " + 
          (WORK_DIR) + "tiles/*.o5m " + 
          (WORK_DIR) + (mapstyle) + "/basemap_typ.txt")


os.chdir(WORK_DIR)
layer = "fixme"

style()

os.chdir("g" + (layer))
printinfo("entered " + os.getcwd())


printinfo((layer) + "-layer build with " + (mapstyle))
os.system("java -ea " + (RAMSIZE) + 
          " -jar " + (mkgmap) +
          " -c " + (WORK_DIR) + "fixme_buglayer.conf " + 
          " --style-file=" + (WORK_DIR) + (mapstyle) + "/fixme_style " +
          " --mapname=" + str(MAPID) + "5001 " +
          " --family-id=3 " +
          " --product-id=33 " + 
          " --description=" + (BUILD_DAY) +
          " --family-name=OSM-Fixme " +
          " --draw-priority=16 " + 
          (WORK_DIR) + "tiles/*.o5m " + 
          (WORK_DIR) + (mapstyle) + "/fixme_typ.txt")
  
"""
  make the dirs to store the images

"""  

dir1 = ((WORK_DIR) + "gps_ready/zipped/" + (BUILD_DAY) + "/")
dir2 = ((WORK_DIR) + "gps_ready/unzipped/" + (BUILD_DAY) + "/")
dir3 = ((WORK_DIR) + "log/" + (BUILD_DAY) + "/")

os.chdir(WORK_DIR)

for dir in [(dir1), (dir2), (dir3)]:
  ExitCode = os.path.exists(dir)
  if ExitCode == True:
    path = (dir) 
    cleanup()
  elif ExitCode == False:
    os.makedirs(dir)

"""
  rename the images

"""  
  
os.chdir(WORK_DIR)
  
for dir in ['gfixme', 'gbasemap']:
  os.system("cp " + (dir) + "/gmapsupp.img "  + 
           (dir2) + (BUILD_MAP) + "_" + (dir) + "_gmapsupp.img")

ExitCode = os.path.exists("hoehenlinien/" + (BUILD_MAP) + "/gmapsupp.img")
if ExitCode == True:
  os.system("cp hoehenlinien/" + (BUILD_MAP) + "/gmapsupp.img " + 
           (dir2) + (BUILD_MAP) + "_gcontourlines_gmapsupp.img")

ExitCode = os.path.exists("tiles/" + (BUILD_MAP) + ".kml")
if ExitCode == True: 
  os.system("mv tiles/" + (BUILD_MAP) + ".kml " + (dir1))
  
ExitCode = os.path.exists("gbasemap/mkgmap.log.0")
if ExitCode == True:
  os.system("mv gbasemap/mkgmap.log.* " + (dir3))
    
    
"""
  zipp the images and mv them to separate dirs

"""
  
os.chdir(dir2)
os.system("for file in *.img; do zip $file.zip $file; done")
os.system("mv *.zip " + (dir1))


printinfo("Habe fertig!")
quit()

""" 

## Changelog:

v0.9.41 - dir for splitter-output

v0.9.40 - more python, removed 'test -[f|d]'

v0.9.38 - mkgmap.org, sitestructure is changed

v0.9.37 - use *.o5m as input for splitter

v0.9.36 - simplify workprocess

v0.9.35 - some changes in workprocess
          some changes at mkgmap-options


"""
