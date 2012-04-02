#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "0.9.21"
__author__ = "Bernd Weigelt, Jonas Stein"
__copyright__ = "Copyright 2011, The OSM-TroLUG-Project"
__credits__ = "Dschuwa"
__license__ = "GPL"
__maintainer__ = "Bernd Weigelt, Jonas Stein"
__email__ = "weigelt.bernd@web.de"
__status__ = "RC"

""" 
  
  pygmap3.py, das script um ein gmapsupp.img für GARMIN-Navigationsgeräte
  zu erzeugen, z.B. Garmin eTrex Vista Hcx
  Ein Gemeinschaftsprojekt von Bernd Weigelt und Jonas Stein
  und als QCO Dschuwa

  License GPL -  read more: www.gnu.org/licenses/licenses.html
  
  
  Work in progress, bitte beachten!
  Prinzipiell funktioniert es, aber wenn was kaputt geht, 
  lehnen wir jegliche Haftung ab.
  
  
  Folgende Software wird benutzt:
  
  mkgmap von 
  http://wiki.openstreetmap.org/wiki/Mkgmap
  
  gmaptool von
  http://www.anpo.republika.pl/download.html
  ~/bin/gmt.exe
 
  splitter von
  http://www.mkgmap.org.uk/page/tile-splitter
  splitter.jar 
 
  osbsql2osm
  erstellt aus Sourcen 
  http://tuxcode.org/john/osbsql2osm/osbsql2osm-latest.tar.gz

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

  return ExitCode


    
# defaults =============================================================================

work_dir = (os.environ['HOME'] + "/share/osm/map_build/") 
# Der letzte Slash muss sein!!!


"""
  argparse
  
"""

parser = argparse.ArgumentParser(
        prog='PROG', 
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\
        
            Als Basis können alle Dateien unter
            http://download.geofabrik.de/osm/
            verwendet werden,dach und benelux sind möglich.
            
            Dateinamen bitte _ohne_ Endung verwenden.
            

            CONTINENT = "europe" (default)
            BUILD_MAP = "germany" (default)
            
            
            Andere Einstellungen können bei Bedarf angepasst werden.
            
            MAP_TYPE = [basemap|freizeitmap|all(default)]
            RAMSIZE = "3000M" or "3G" (default)
            MAXNODES = "1000000" (default)
            MKGMAP_VERSION = use a defined mkgmap-version, 
                             for available versions
                             http://www.mkgmap.org.uk/snapshots/
            SPLITTER_VERSION = same as before for splitter    
            
        '''))

parser.add_argument('-c', '--continent', dest='continent', default='europe')
parser.add_argument('-b', '--buildmap', dest='build_map', default='germany')
parser.add_argument('-t', '--type', dest='map_type', default='all')
parser.add_argument('-r', '--ramsize', dest='ramsize', default='3G')
parser.add_argument('-m', '--maxnodes', dest='maxnodes', default='1000000')
parser.add_argument('-mkv', '--mkgmap_version', dest='mkgmap_version', default=0)
parser.add_argument('-spv', '--splitter_version', dest='splitter_version', default=0)
args = parser.parse_args()


CONTINENT = (args.continent)
BUILD_MAP = (args.build_map)
MAP_TYPE = (args.map_type)
PREFIX = "-Xmx"
RAMSIZE = ((PREFIX) + (args.ramsize))
MAXNODES = (args.maxnodes)
MKGMAP_VERSION = (args.mkgmap_version)
SPLITTER_VERSION = (args.splitter_version)
"""
  needed programs und dirs
  
"""

hint = ("mkdir " + (work_dir))
checkdir((work_dir), hint) 

hint = "Install: wine to work with ~/bin/gmt.exe from GMAPTOOLS"
checkprg("wine", hint)
 
hint = " Download: http://www.anpo.republika.pl/download.html"
checkprg("~/bin/gmt.exe", hint)
 
hint = "Download:  http://tuxcode.org/john/osbsql2osm/osbsql2osm-latest.tar.gz"
checkprg("osbsql2osm", hint)

hint = "Install: 7z to extract mkgmap's sStylefiles"
checkprg("7z", hint)

hint = " gpsbabel fehlt, wird gebraucht zur Verarbeitung der OSB als bz2! "
checkprg("gpsbabel", hint)

hint = " osmconvert fehlt, wird gebraucht zum Erstellen von Kartenbündeln wie DACH"
checkprg("osmconvert", hint)

os.chdir(work_dir)
  
 
""" 
  get the contourlines for Germany, if not present
  other countries could be found at openmtb.org
  please build the gmapsupp.img for every country in own folders and store it
  in hoehenlinien/(buildmap)/gmapsupp.img
  
"""
if (BUILD_MAP) == "germany":
  ExitCode  = os.system("test -d gcontourlines")
  if ExitCode != 0:
      os.system("rm -Rf gcontourlines")
      os.makedirs("gcontourlines/temp")
      os.chdir("gcontourlines/temp")
      os.system("wget \
              -N http://www.glade-web.de/GLADE_geocaching/maps/TOPO_D_SRTM.zip")
      os.system("unzip Topo_D_SRTM.zip")
      os.system("wine ~/bin/gmt.exe -j -f 5,25 -m HOEHE -o \
                ../gmapsupp.img Topo\ D\ SRTM/*.img")
      os.chdir("..")
      os.system("rm -Rf temp")
      os.chdir(work_dir)

""" 
  get the styles, 7z is needed to extract the styles

"""   
   
ExitCode = os.system("test -d aiostyles")
    
if ExitCode == 0:
  os.chdir(work_dir)

else:
  os.system("wget http://dev.openstreetmap.de/aio/aiostyles.7z")
  os.system("7z x aiostyles.7z -oaiostyles")
  os.chdir(work_dir)

"""
  get splitter and mkgmap 
  
"""  
target = http.client.HTTPConnection("www.mkgmap.org.uk")

if SPLITTER_VERSION != 0:
  ExitCode = os.system("test -d splitter-r" + (SPLITTER_VERSION))
  if ExitCode != 0:
    os.system(("wget -N http://www.mkgmap.org.uk/snapshots/splitter-r") + 
	      (SPLITTER_VERSION) + (".tar.gz"))
    tar = tarfile.open((work_dir) + "splitter-r" + (SPLITTER_VERSION) + (".tar.gz"))
    tar.extractall()
    tar.close()   
  
  splitter = ((work_dir) + "splitter-r" + (SPLITTER_VERSION) + "/splitter.jar")
  
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
  tar = tarfile.open((work_dir) + (splitter_rev) + (".tar.gz"))
  tar.extractall()
  tar.close()    
    
  splitter = ((work_dir) + (splitter_rev) + "/splitter.jar")

if MKGMAP_VERSION != 0:
  ExitCode = os.system("test -d mkgmap-r" + (MKGMAP_VERSION))
  if ExitCode != 0:
    os.system(("wget -N http://www.mkgmap.org.uk/snapshots/mkgmap-r") + 
              (MKGMAP_VERSION) + (".tar.gz"))
    tar = tarfile.open((work_dir) + "mkgmap-r" + (MKGMAP_VERSION) + (".tar.gz"))
    tar.extractall()
    tar.close()
  
  mkgmap = (work_dir) + "mkgmap-r" + (MKGMAP_VERSION) + "/mkgmap.jar"
  

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
  tar = tarfile.open((work_dir) + (mkgmap_rev) + (".tar.gz"))
  tar.extractall()
  tar.close()

  mkgmap = (work_dir) + (mkgmap_rev) + "/mkgmap.jar"

target.close()

""" 
  get the OpenStreetBugs
  
"""  

os.system("wget -N   \
           http://openstreetbugs.schokokeks.org/dumps/osbdump_latest.sql.bz2")
os.system("bzcat osbdump_latest.sql.bz2 | osbsql2osm > OpenStreetBugs.osm")


"""
  get the raw map-extracts from the geofabrik
  
"""  
if (BUILD_MAP) == "dach":
    for i in ['germany', 'austria', 'switzerland']:
      os.system("wget -N http://download.geofabrik.de/osm/europe/" + (i) + ".osm.pbf")
    os.system("osmconvert austria.osm.pbf -o=austria.o5m && osmconvert germany.osm.pbf -o=germany.o5m && osmconvert switzerland.osm.pbf -o=switzerland.o5m && osmconvert austria.o5m germany.o5m switzerland.o5m -o=dach.osm.pbf")
    
elif (BUILD_MAP) == "benelux":  
    for i in ['netherlands', 'belgium', 'luxembourg']:
      os.system("wget -N http://download.geofabrik.de/osm/europe/" + (i) + ".osm.pbf")
    os.system("osmconvert netherlands.osm.pbf -o=netherlands.o5m && osmconvert belgium.osm.pbf -o=belgium.o5m && osmconvert luxembourg.osm.pbf -o=luxembourg.o5m && osmconvert netherlands.o5m belgium.o5m luxembourg.o5m -o=benelux.osm.pbf")    

else:  
   os.system("wget -N http://download.geofabrik.de/osm/" + (CONTINENT) + "/" + 
            (BUILD_MAP) + ".osm.pbf")


"""
  create (work_dir) for splitter
  
"""  
 
ExitCode = os.system("test -d tiles")

if ExitCode == 0:
  os.chdir("tiles")
  os.system("rm -Rf *.pbf")
  os.chdir(work_dir)
	  
else: 
    os.mkdir("tiles")

    
"""
  Zufällige mapid, damit mehrere Karten verwendet werden können,
  alternativ könnte man eine Liste erstellen
"""

MAPID = random.randint(6301, 6399)


"""
  split rawdata
  
"""
os.chdir("tiles")
os.system("java -ea " + (RAMSIZE) + " -jar " + (splitter) + 
           " --mapid=" + str(MAPID) + "0001 --max-nodes=" + (MAXNODES) + 
           " --cache=cache " + (work_dir) + (BUILD_MAP) + ".osm.pbf")
os.chdir(work_dir)


"""
  create mapdirs
  
"""

for dir in ['gfixme', 'gosb', 'gbasemap', 'gboundary', 'gfreizeitmap', 
            'gaddr', 'gps_ready']:
  ExitCode = os.system("test -d " + (dir))
  if ExitCode != 0:
    os.mkdir(dir)

"""
  add your own styles in mystyles
  
"""

def style():
  os.chdir(work_dir)
  ExitCode = os.system("test -d " + (work_dir) + "mystyles/" + 
                         (layer) + "_style")
  global mapstyle
  if ExitCode == 0:
    mapstyle = "mystyles"
  else:
    mapstyle = "aiostyles"
  
def cleanup():  
  os.chdir((work_dir) + "/g" + (layer))
  print((layer) + "-layer build with " + (mapstyle))
  os.system("rm -Rf * ")
  os.system("ln -s ../bounds bounds")
  
""" 
 create Bugs- and FIXME-Layer 
 
"""

layer = "addr"
style()
cleanup()
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + 
          (work_dir) + "fixme_buglayer.conf --style-file=" + 
          (work_dir) + (mapstyle) + "/addr_style --description=OSMaddr \
          --family-id=5 --product-id=40 --series-name=OSMadresses  \
          --family-name=OSMaddr --mapname=" + str(MAPID) + "4001 --draw-priority=12 " + 
          (work_dir) + "tiles/*.osm.pbf " + 
          (work_dir) + (mapstyle) +"/addr.TYP")

layer = "boundary"
style()
cleanup()
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + 
          (work_dir) + "fixme_buglayer.conf --style-file=" + 
          (work_dir) + (mapstyle) + "/boundary_style --description=OSMboundary \
          --family-id=6 --product-id=30 --series-name=OSMboundary  \
          --family-name=OSMboundary --mapname=" + str(MAPID) + "5001 --draw-priority=14 " + 
          (work_dir) + "tiles/*.osm.pbf " + 
          (work_dir) + (mapstyle) + "/boundary.TYP")

layer = "fixme"
style()
cleanup()
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + 
          (work_dir) + "fixme_buglayer.conf --style-file=" + 
          (work_dir) + (mapstyle) + "/fixme_style --description=OSMfixme  \
          --family-id=3 --product-id=33 --series-name=OSMfixme  \
          --family-name=OSMfixme --mapname=" + str(MAPID) + "6001 --draw-priority=16 " + 
          (work_dir) + "tiles/*.osm.pbf " + 
          (work_dir) + (mapstyle) + "/fixme.TYP")

layer = "osb"
style()
cleanup()
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + 
          (work_dir) + "fixme_buglayer.conf --style-file=" + 
          (work_dir) + (mapstyle) + "/osb_style --description=OpenStreetBugs \
          --family-id=2323 --product-id=42 --series-name=OSMbugs \
          --family-name=OSMbugs --mapname=" + str(MAPID) + "7001 --draw-priority=18 " + 
          (work_dir) + "OpenStreetBugs.osm " + 
          (work_dir) + (mapstyle) + "/osb.TYP")
os.chdir(work_dir)

"""
  destination separated for country and day
  
"""

today = datetime.datetime.now()
day = today.strftime('%Y_%m_%d')
  
dir1 = ("gps_ready/" + (CONTINENT) + "/" + (BUILD_MAP) + "/" + (day))
dir2 = ("gps_ready/unzipped/" + (CONTINENT) + "/"  + (BUILD_MAP) + "/" + (day))

"""
  diverse Definitionen
  
"""  
  
def mk_store():
  os.chdir(work_dir)
  for dir in [(dir1), (dir2)]:
    ExitCode = os.system("test -d " +  (dir))
    if ExitCode == 0:
      os.system("rm -Rf " + (dir)) 
      os.makedirs(dir)
    elif ExitCode != 0:
      os.makedirs(dir)

  
def basemap():
  global layer
  layer = "basemap"
  style()
  cleanup()
  os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + 
            (work_dir) + "map.conf --style-file=" + 
            (work_dir) + (mapstyle) + "/basemap_style --description=basemap  \
            --family-id=4 --product-id=45 --series-name=OSMbasemap  \
            --family-name=OSMbasemap --mapname=" + str(MAPID) + "2001 --draw-priority=10 " + 
            (work_dir) + "tiles/*.osm.pbf " + 
            (work_dir) + (mapstyle) + "/basemap.TYP")
  os.chdir(work_dir)
                         
                         
def freizeitmap():
  global layer
  layer = "freizeitmap"
  style()
  cleanup()
  os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + 
            (work_dir) + "map.conf --style-file=" + 
            (work_dir) + (mapstyle) + "/freizeitmap_style --description=freizeitmap  \
            --family-id=5824 --product-id=1 --series-name=OSMfreizeitmap  \
            --family-name=OSMfreizeitmap --mapname=" + str(MAPID) + "3001 --draw-priority=10 " + 
            (work_dir) + "tiles/*.osm.pbf " + 
            (work_dir) + (mapstyle) + "/freizeitmap.TYP")
  os.chdir(work_dir)
    
###  Wenn nur die einzelne Karten gewählt wurden

def merge():
  os.chdir(work_dir)
  if (BUILD_MAP) == "germany":
    os.system("wine ~/bin/gmt.exe -jo " + 
              (work_dir) + "gps_ready/unzipped/" + 
              (CONTINENT) + "/"  + (BUILD_MAP) + "/" + (day) + "/" + 
              (BUILD_MAP) + "_full_" + (MAP_TYPE) + "_gmapsupp.img  \
              g" + (MAP_TYPE) + "/gmapsupp.img  \
              gaddr/gmapsupp.img  \
              gboundary/gmapsupp.img  \
              gosb/gmapsupp.img  \
              gfixme/gmapsupp.img  \
              gcontourlines/gmapsupp.img")
              
  elif (BUILD_MAP) != "germany":
    ExitCode = os.system("test -d hoehenlinien/" + (BUILD_MAP))
    if ExitCode == 0:
      os.system("wine ~/bin/gmt.exe -jo " + 
              (work_dir) + "gps_ready/unzipped/" + 
              (CONTINENT) + "/"  + (BUILD_MAP) + "/" + (day) + "/" + 
              (BUILD_MAP) + "_full_" + (MAP_TYPE) + "_gmapsupp.img  \
              g" + (MAP_TYPE) + "/gmapsupp.img  \
              gaddr/gmapsupp.img  \
              gboundary/gmapsupp.img  \
              gosb/gmapsupp.img  \
              gfixme/gmapsupp.img  \
              hoehenlinien/" + (BUILD_MAP) + "/gmapsupp.img")
              
    else:
      os.system("wine ~/bin/gmt.exe -jo " + 
                (work_dir) + "gps_ready/unzipped/" + 
                (CONTINENT) + "/"  + (BUILD_MAP) + "/" + (day) + "/" + 
                (BUILD_MAP) + "_full_" + (MAP_TYPE) + "_gmapsupp.img  \
                g" + (MAP_TYPE) + "/gmapsupp.img  \
                gaddr/gmapsupp.img  \
                gboundary/gmapsupp.img  \
                gosb/gmapsupp.img  \
                gfixme/gmapsupp.img")

###  Erstellen der verschiedenen Images

def merge_all():
  for map in ['basemap', 'freizeitmap']:
    os.chdir(work_dir)
    if (BUILD_MAP) == "germany":
      os.system("wine ~/bin/gmt.exe -jo " +
                (work_dir) + "gps_ready/unzipped/" +
                (CONTINENT) + "/"  + (BUILD_MAP) + "/" + (day) + "/"  + 
                (BUILD_MAP) + "_full_" + (map) + "_gmapsupp.img  \
                g" + (map) + "/gmapsupp.img  \
                gaddr/gmapsupp.img  \
                gboundary/gmapsupp.img  \
                gosb/gmapsupp.img  \
                gfixme/gmapsupp.img  \
                gcontourlines/gmapsupp.img")

    elif (BUILD_MAP) != "germany":
      ExitCode = os.system("test -d hoehenlinien/" + (BUILD_MAP))
      if ExitCode == 0:
        os.system("wine ~/bin/gmt.exe -jo " + 
                  (work_dir) + "gps_ready/unzipped/" +
                  (CONTINENT) + "/"  + (BUILD_MAP) + "/" + (day) + "/"  + 
                  (BUILD_MAP) + "_full_" + (map) + "_gmapsupp.img  \
                  g" + (map) + "/gmapsupp.img  \
                  gaddr/gmapsupp.img  \
                  gboundary/gmapsupp.img   \
                  gosb/gmapsupp.img  \
                  gfixme/gmapsupp.img  \
                  hoehenlinien/" + (BUILD_MAP) + "/gmapsupp.img")
                  
      else:
        os.system("wine ~/bin/gmt.exe -jo " + 
                  (work_dir) + "gps_ready/unzipped/" + 
                  (CONTINENT) + "/"  + (BUILD_MAP) + "/" + (day) + "/"  + 
                  (BUILD_MAP) + "_full_" + (map) + "_gmapsupp.img  \
                  g" + (map) + "/gmapsupp.img  \
                  gaddr/gmapsupp.img  \
                  gboundary/gmapsupp.img  \
                  gosb/gmapsupp.img  \
                  gfixme/gmapsupp.img") 

###  Umkopieren der Images

def copy_parts():
  os.chdir(work_dir)
  for dir in ['gfixme', 'gosb', 'gboundary', 'gaddr', 'gbasemap', 'gfreizeitmap' ]:
    os.system("cp " + (dir) + "/gmapsupp.img "  + 
             (work_dir) + "gps_ready/unzipped/" + 
             (CONTINENT) + "/"  + (BUILD_MAP) + "/" + (day) + "/"  + 
             (BUILD_MAP) + "_parts_" + (dir) + "_gmapsupp.img")
             
  ExitCode = os.system("test -f " + (work_dir) + "gps_ready/unzipped/" + 
             (CONTINENT) + "/" + (BUILD_MAP) + "/" + (day) + "/"  + 
             (BUILD_MAP) + "_parts_gcontourlines_gmapsupp.img")    
  if ExitCode != 0:
    if (BUILD_MAP) != "germany":
      ExitCode = os.system("test -d hoehenlinien/" + (BUILD_MAP))
      if ExitCode == 0:
        os.system("cp " + (work_dir) + "hoehenlinien/" + 
             (BUILD_MAP) + "/gmapsupp.img " + 
             (work_dir) + "gps_ready/unzipped/" + 
             (CONTINENT) + "/"  + (BUILD_MAP) + "/" + (day) + "/"  + 
             (BUILD_MAP) + "_parts_gcontourlines_gmapsupp.img") 
    elif (BUILD_MAP) == "germany":
      os.system("cp " + (work_dir) + "gcontourlines/gmapsupp.img " + 
                (work_dir) + "gps_ready/unzipped/" + 
                (CONTINENT) + "/"  + (BUILD_MAP) + "/" + (day) + "/"  + 
                (BUILD_MAP) + "_parts_gcontourlines_gmapsupp.img")   

###  Komprimieren der Images und Kopieren der Zips in ein separates Verzeichnis

def zip_file():
  os.chdir(work_dir) 
  os.chdir(dir2)
  os.system("for file in *.img; do zip $file.zip $file; done")
  os.system("mv *.zip " + (work_dir) + (dir1))
  

"""
  Ausführen der o.g. defs zum erstellen der Karten
  
"""

if (MAP_TYPE) == "all":
  mk_store()  
  basemap()
  freizeitmap()
  merge_all()
  copy_parts()
  zip_file()

elif (MAP_TYPE) == "basemap":
  mk_store()
  basemap()
  merge()
  zip_file()

elif (MAP_TYPE) == "freizeitmap":
  mk_store()
  freizeitmap()
  merge()
  zip_file()  
  


printinfo("Habe fertig!")

""" 

## Changelog:

v0.9.21 - predefined bundles of maps like DACH or Benelux

v0.9.20 - removed velomap-code 
	  use 7z for styles
	  removed git-code
	  some cleanups

v0.9.17 - Zufallszahlen für mapid

v0.9.16 - Freizeitkarte hinzugefügt copyright siehe 
          http://www.easyclasspage.de/karten/index.html

v0.9.15 - Anpassung der Kachelnummerierung für Splitter, beginnt jetzt bei 0001
          statt 0023

v0.9.14 - cleanups

v0.9.12 - options to change mapid 

v0.9.10	- offline-mode for splitter and mkgmap

v0.9.9	- defined mkgmap-version

v0.9.8	- added bounds-support

v0.9.7	- removed use of osm.bz2 and osm.gz, use osm.pbf as 
          new default by splitter, 
	- cleanups and comments

v0.9.6	- added function to set another continent

v0,9.5	- Umstieg auf Python 3.2.x 
	- commandline-otions added with argparse
	- Umformatierung langer Zeilen

v0.9.4	- cleanups

v0.9.3	- sepatated folder for the maps

v0.9.2	- addr- and boundary-layer added

v0.9.1	- zip-function added

## 2011-05-01 Projectstatus changed to RC

v0.8.5	- minor fixes

v0.8.3	- add contourlines to gps_parts if available

v0.8.2	- code cleanup, dirs added gps_parts and gps_ready

v0.8.1	- separate Images for 'all' 

v0.8.0	- AIO-basemap as additional maptype

## 2011-02-14 Projectstatus changed to BETA

v0.7.1	- minor fixes

v0.7.0	- download *.pbf (osmosis) or *.bz2, check osbsql2osm to use OSB-database-dumps

v0.6.8	- Cleanups

v0.6.7	- change work_dir to map_build

v0.6.6	- better map-description, if more then one map is used on the GPS-device


v0.6.1	- first working version with python3, but there are a lot of things to do,
	  next is make it use startoptions and the pygmap.conf to remember these options
	  there are many systemcalls, which only work on Linux, they must be changed
	  removed many comments and code from the bash, because they make it unreadable

v0.6.0 	- Beginn der Umstellung auf python, aktuell noch nicht benutzbar

"""
