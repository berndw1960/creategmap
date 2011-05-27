#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "0.9.3"
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


    
# VARs =============================================================================


"""
  Diese Funktion sollte bestehen bleiben, um entweder bei Erstbenutzung
  ausführliche Infos zu geben, und eventuell die Möglichkeit des Rücksetzen
  auf die Default-Einstellungen bei Fehlern zu bieten
"""
verbose = 1 ## default '= 1' an dieser Stelle


work_dir = (os.environ['HOME'] + "/share/osm/map_build/") # Der letzte Slash muss sein!!!

RAMSIZE_DEFAULT = "-Xmx6000M"
MAXNODES_DEFAULT = "1200000"

BUILD_MAP_DEFAULT = "germany"

MAP_TYPE_DEFAULT = "all"


## needed programs und dirs

hint = ("mkdir " + (work_dir))
checkdir((work_dir), hint) 

hint = "Install: wine to work with ~/bin/gmt.exe from GMAPTOOLS"
checkprg("wine", hint)
 
hint = " Download: http://www.anpo.republika.pl/download.html "
checkprg("~/bin/gmt.exe", hint)
 
hint = "Download:  http://tuxcode.org/john/osbsql2osm/osbsql2osm-latest.tar.gz"
checkprg("osbsql2osm", hint)

hint = " git fehlt, wird gebraucht um die mkgmap-Styles zu holen! "
checkprg("git", hint)

hint = " osmosis fehlt, wird gebraucht zur Verarbeitung der *.pbf files! "
checkprg("osmosis", hint)

hint = " gpsbabel fehlt, wird gebraucht zur Verarbeitung der OSB als bz2! "
checkprg("gpsbabel", hint)



os.chdir(work_dir)


if  verbose == 1:

  print(""" 
	  
	   
	        Welche Art von Karte soll erstellt werden?
	        
	        Möglich sind die 
	        velomap  		gmapsupp.img
	        basemap 		gmapsupp.img
	        all (Standard)		Einzelimages für neuere Garmingeräte 
					und gmapsupp.img für die älteren.
		
		Zusätzlich werden immer aktuelle OSB- und fixme-Layer erstellt.
	  
  """)
  print("                Vorgabewert: ", (MAP_TYPE_DEFAULT))
  MAP_TYPE = input("                Bitte die gewünschte Kartenart eingeben: ")
    
  if MAP_TYPE == "":
    MAP_TYPE = (MAP_TYPE_DEFAULT)

        
  print("                Wahl:        ", MAP_TYPE)



  print(""" 
	  
	   
	        Bitte beachten!"
	        Erstellen von Karten für einzelne Bundesländer ist nicht möglich,
	        diese können über die AIO-Downloadseite gefunden werden.
	   
	  
	        Mögliche Länder finden Sie unter http://download.geofabrik.de/osm/europe/.
	        
	        Bitte nur den Dateinamen ohne Endung!
	  
  """)
  print("                Vorgabewert: ", (BUILD_MAP_DEFAULT))
  BUILD_MAP = input("                Bitte die gewünschte Karte eingeben: ")
    
  if BUILD_MAP == "":
    BUILD_MAP = (BUILD_MAP_DEFAULT)
    
  print("                Wahl:        ", BUILD_MAP)



  print(""" 
		
		Abhängig vom vorhandenen RAM muß die Menge des Speichers 
		für Java eingestellt werden.
		Unter 1 GiB dürfte eine Kartenerstellung nicht möglich sein.
		Empfohlen werden mindestens 2 GiB RAM!"
		
  """)
  print("                Vorgabewert: ", (RAMSIZE_DEFAULT)) 
  RAMSIZE = input("                Wieviel Speicher soll verwendet werden? ")

  if RAMSIZE == "":
    RAMSIZE = (RAMSIZE_DEFAULT)  
  print("                Wahl:        ", (RAMSIZE)) 

  print(""" 
		
		Bei kleineren Karten können die Werte für die MAXNODES bei Splitter eventuell 
		heraufgesetzt werden, große Karten wie Deutschland und Frankreich sollten mit 
		den folgenden Vorschlagswerten erstellt werden.

		2 GiB (-Xmx2000M) -->	 500000
		4+GiB (-Xmx4000M) -->	1000000
		
  """)       
  print("                Vorgabewert: ", (MAXNODES_DEFAULT))
  MAXNODES = input("                Bitte Anzahl der gewünschten Nodes eingeben: ")
    
  if MAXNODES == "":
    MAXNODES = (MAXNODES_DEFAULT)

  print("                Wahl:        ", (MAXNODES))




    
 
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
      os.mkdir("gcontourlines")
      os.chdir("gcontourlines")
      os.mkdir("temp")
      os.chdir("temp")
      os.system("wget -N http://www.glade-web.de/GLADE_geocaching/maps/TOPO_D_SRTM.zip")
      os.system("unzip Topo_D_SRTM.zip")
      os.system("wine ~/bin/~/bin/gmt.exe -j -f 5,25 -m HOEHE -o ../gmapsupp.img Topo\ D\ SRTM/*.img")
      os.chdir("..")
      os.system("rm -Rf temp")
      os.chdir(work_dir)

""" 
  get the styles for base- and velomap with git

"""   
   
ExitCode = os.system("test -d aiostyles")
    
if ExitCode == 0:
  os.chdir("aiostyles")
  os.system("git pull")
  os.chdir(work_dir)

else:
  os.system("git clone git://github.com/aiomaster/aiostyles.git")
  os.chdir(work_dir)

##  get mkgmap and splitter
  

target = http.client.HTTPConnection("www.mkgmap.org.uk")

target.request("GET", "/snapshots/index.html")
htmlcontent =  target.getresponse()
print(htmlcontent.status, htmlcontent.reason)
data = htmlcontent.read()
data = data.decode('utf8')
pattern = re.compile('mkgmap-r\d{4}')
mkgmap_rev = sorted(pattern.findall(data), reverse=True)[1]


target.request("GET", "/splitter/index.html")
htmlcontent =  target.getresponse()
print(htmlcontent.status, htmlcontent.reason)
data = htmlcontent.read()
data = data.decode('utf8')
pattern = re.compile('splitter-r\d{3}')
splitter_rev = sorted(pattern.findall(data), reverse=True)[1]

target.close()

os.system(("wget -N http://www.mkgmap.org.uk/snapshots/") + (mkgmap_rev) + (".tar.gz"))  

tar = tarfile.open((work_dir) + (mkgmap_rev) + (".tar.gz"))
tar.extractall()
tar.close()
    
mkgmap = (work_dir) + (mkgmap_rev) + "/mkgmap.jar"


os.system(("wget -N http://www.mkgmap.org.uk/splitter/") + (splitter_rev) + (".tar.gz"))

tar = tarfile.open((work_dir) + (splitter_rev) + (".tar.gz"))
tar.extractall()
tar.close()    
    
splitter = ((work_dir) + (splitter_rev) + "/splitter.jar")


""" 
  get the OpenStreetBugs
  
"""  
ExitCode = os.system("which osbsql2osm")
if ExitCode == 0:
  os.system("wget -N http://openstreetbugs.schokokeks.org/dumps/osbdump_latest.sql.bz2")
  os.system("bzcat osbdump_latest.sql.bz2 | osbsql2osm > OpenStreetBugs.osm")
else:
  os.system("wget -N http://www.gary68.de/osm/qa/gpx/allbugs.gpx --output-document=OpenStreetBugs.gpx")
  os.system("gpsbabel -i gpx -o osm OpenStreetBugs.gpx OpenStreetBugs.osm")



# cleanup

ExitCode = os.system("test -f " + (BUILD_MAP) + ".osm")

if ExitCode == 0:
  os.remove((BUILD_MAP) + ".osm")

ExitCode = os.system("which osmosis")

if ExitCode == 0:
  os.system("wget -N http://download.geofabrik.de/osm/europe/" + (BUILD_MAP) + ".osm.pbf")
  os.system("osmosis --read-bin " + (BUILD_MAP) + ".osm.pbf --write-xml " + (BUILD_MAP) + ".osm")

else:
  os.system("wget -N http://download.geofabrik.de/osm/europe/" + (BUILD_MAP) + ".osm.bz2")   
  os.system("bunzip2 -k " + (BUILD_MAP) + ".osm.bz2")


##  create (work_dir) for splitter
 
ExitCode = os.system("test -d tiles")

if ExitCode == 0:
  os.chdir("tiles")
  os.system("rm -Rf *")
  os.chdir(work_dir)
	  
else: 
    os.mkdir("tiles")
             
## split rawdata

os.chdir("tiles")
os.system("java -ea " + (RAMSIZE) + " -jar " + (splitter) + " --mapid=63240023 --max-nodes=" + (MAXNODES) + " --cache=cache " + (work_dir) + (BUILD_MAP) + ".osm")
os.chdir(work_dir)

## create mapdirs

for dir in ['gfixme', 'gosb', 'gvelomap', 'gbasemap', 'gboundary', 'gaddr', 'gps_ready']:
  ExitCode = os.system("test -d " + (dir))
  if ExitCode != 0:
    os.mkdir(dir)
      
""" 
 create Bugs- and FIXME-Layer 


"""
os.system("rm -Rf gfixme/* gosb/* ")

## add your own styles for OSB and FIXMEs in mystyles 
ExitCode = os.system("test -d " + (work_dir) + "mystyles/fixme_style")
    
if ExitCode == 0:    
  mapstyle_fixme = "mystyles"
else:
  mapstyle_fixme = "aiostyles" 

print(mapstyle_fixme)

os.chdir((work_dir) + "gfixme")

print(os.getcwd())
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + (work_dir) + "fixme_buglayer.conf --style-file=" + (work_dir) + (mapstyle_fixme) + "/fixme_style --description=fixme --family-id=3 --product-id=33 --series-name=OSMfixme --family-name=OSMfixme --mapname=63244023 --draw-priority=16 " + (work_dir) + "tiles/*.osm.gz " + (work_dir) + (mapstyle_fixme) + "/fixme.TYP")

ExitCode = os.system("test -d " + (work_dir) + "mystyles/osb_style")
    
if ExitCode == 0:    
  mapstyle_osb = "mystyles"
else:
  mapstyle_osb = "aiostyles" 

print(mapstyle_osb)

os.chdir((work_dir) + "/gosb")

print(os.getcwd())
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + (work_dir) + "fixme_buglayer.conf --style-file=" + (work_dir) + (mapstyle_osb) + "/osb_style --description=osb --family-id=2323 --product-id=42 --series-name=OSMbugs --family-name=OSMbugs --mapname=63245023 --draw-priority=14 " + (work_dir) + "OpenStreetBugs.osm " + (work_dir) + (mapstyle_osb) + "/osb.TYP")

os.chdir(work_dir)

os.chdir((work_dir) + "/gaddr")

print(os.getcwd())
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + (work_dir) + "fixme_buglayer.conf --style-file=" + (work_dir) + "aiostyles/addr_style --description=addr --family-id=5 --product-id=40 --series-name=OSMAdressen --family-name=OSMaddr --mapname=63242023 --draw-priority=14 " + (work_dir) + "tiles/*.osm.gz " + (work_dir) + "aiostyles/addr.TYP")

os.chdir(work_dir)

os.chdir((work_dir) + "/gboundary")

print(os.getcwd())
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + (work_dir) + "fixme_buglayer.conf --style-file=" + (work_dir) + "aiostyles/boundary_style --description=boundary --family-id=6 --product-id=30 --series-name=OSMboundary --family-name=OSMboundary --mapname=63243023 --draw-priority=14 " + (work_dir) + "tiles/*.osm.gz " + (work_dir) + "aiostyles/boundary.TYP")

os.chdir(work_dir)


## destination separated for country and day

today = datetime.datetime.now()
day = today.strftime('%Y_%m_%d')
  
dir1 = ("gps_ready/" + (BUILD_MAP) + "/" + (day))
dir2 = ("gps_ready/unzipped/" + (BUILD_MAP) + "/" + (day))


def mk_store():
  os.chdir(work_dir)
  for dir in [(dir1), (dir2)]:
    ExitCode = os.system("test -d " +  (dir))
    if ExitCode == 0:
      os.system("rm -Rf " + (dir)) 
      os.makedirs(dir)
    elif ExitCode != 0:
      os.makedirs(dir)
    
    
## look for mkgmap's special version for the velomap and then build the maps
def velomap():
  os.chdir(work_dir)
  ExitCode = os.system("test -f aiostyles/mkgmap_velo.jar")
  if ExitCode == 0:
    mkgmap_velo = (work_dir) + "aiostyles/mkgmap_velo.jar"
        
  else:
    mkgmap_velo = (mkgmap)

  os.chdir("gvelomap")
  os.system("rm -Rf * ")
  print(os.getcwd())
  os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap_velo) + " -c " + (work_dir) + "velomap.conf --style-file=" + (work_dir) + "aiostyles/velomap_style --description=velomap --family-id=6365 --product-id=1 --series-name=OSMvelomap --family-name=OSMvelomap --mapname=63241023 --draw-priority=12 " + (work_dir) + "tiles/*.osm.gz " + (work_dir) + "aiostyles/velomap.TYP")
  os.chdir(work_dir)
    
def basemap():
  os.chdir(work_dir)  
  os.chdir("gbasemap")
  os.system("rm -Rf * ")
  print(os.getcwd())
  os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + (work_dir) + "basemap.conf --style-file=" + (work_dir) + "aiostyles/basemap_style --description=basemap --family-id=4 --product-id=45 --series-name=OSMbasemap --family-name=OSMbasemap --mapname=63240023 --draw-priority=10 " + (work_dir) + "tiles/*.osm.gz " + (work_dir) + "aiostyles/basemap.TYP")
  os.chdir(work_dir)

## Wenn nur die base- oder velomap gewählt wurde
def merge():
  os.chdir(work_dir)
  if (BUILD_MAP) == "germany":
    os.system("wine ~/bin/gmt.exe -jo " + (work_dir) + "gps_ready/unzipped/" + (BUILD_MAP) + "_" + (MAP_TYPE) + "_full_gmapsupp.img g" + (MAP_TYPE) + "/gmapsupp.img gaddr/gmapsupp.img gboundary/gmapsupp.img gosb/gmapsupp.img gfixme/gmapsupp.img gcontourlines/gmapsupp.img")
  elif (BUILD_MAP) != "germany":
    ExitCode = os.system("test -d hoehenlinien/" + (BUILD_MAP))
    if ExitCode == 0:
      os.system("wine ~/bin/gmt.exe -jo " + (work_dir) + "gps_ready/unzipped/" + (BUILD_MAP) + "_" + (MAP_TYPE) + "_full_gmapsupp.img g" + (MAP_TYPE) + "/gmapsupp.img gaddr/gmapsupp.img gboundary/gmapsupp.img gosb/gmapsupp.img gfixme/gmapsupp.img hoehenlinien/" + (BUILD_MAP) + "/gmapsupp.img")
    else:
      os.system("wine ~/bin/gmt.exe -jo " + (work_dir) + "gps_ready/unzipped/" + (BUILD_MAP) + "_" + (MAP_TYPE) + "_full_gmapsupp.img g" + (MAP_TYPE) + "/gmapsupp.img gaddr/gmapsupp.img gboundary/gmapsupp.img gosb/gmapsupp.img gfixme/gmapsupp.img")

## falls _alle_ Karten erstellt werden (default)
def merge_all():
  for map in ['velomap', 'basemap']:
    os.chdir(work_dir)
    if (BUILD_MAP) == "germany":
      os.system("wine ~/bin/gmt.exe -jo " + (work_dir) + "gps_ready/unzipped/" + (BUILD_MAP) + "/" + (day) + "/"  + (BUILD_MAP) + "_" + (map) + "_full_gmapsupp.img g" + (map) + "/gmapsupp.img gaddr/gmapsupp.img gboundary/gmapsupp.img gosb/gmapsupp.img gfixme/gmapsupp.img gcontourlines/gmapsupp.img")
    elif (BUILD_MAP) != "germany":
      ExitCode = os.system("test -d hoehenlinien/" + (BUILD_MAP))
      if ExitCode == 0:
        os.system("wine ~/bin/gmt.exe -jo " + (work_dir) + "gps_ready/unzipped/" + (BUILD_MAP) + "/" + (day) + "/"  + (BUILD_MAP) + "_" + (map) + "_full_gmapsupp.img g" + (map) + "/gmapsupp.img gaddr/gmapsupp.img gboundary/gmapsupp.img gosb/gmapsupp.img gfixme/gmapsupp.img hoehenlinien/" + (BUILD_MAP) + "/gmapsupp.img")
      else:
        os.system("wine ~/bin/gmt.exe -jo " + (work_dir) + "gps_ready/unzipped/" + (BUILD_MAP) + "/" + (day) + "/"  + (BUILD_MAP) + "_" + (map) + "_full_gmapsupp.img g" + (map) + "/gmapsupp.img gaddr/gmapsupp.img gboundary/gmapsupp.img gosb/gmapsupp.img gfixme/gmapsupp.img")

## diverse einzelne Layer für neuere garmin
def copy_parts():
  os.chdir(work_dir)
  for dir in ['gfixme', 'gosb', 'gboundary', 'gaddr', 'gvelomap', 'gbasemap']:
    os.system("cp " + (dir) + "/gmapsupp.img "  + (work_dir) + "gps_ready/unzipped/" + (BUILD_MAP) + "/" + (day) + "/"  + (BUILD_MAP) + "_" + (dir) + "_parts_gmapsupp.img")
  ExitCode = os.system("test -f " + (work_dir) + "gps_ready/unzipped/" + (BUILD_MAP) + "/" + (day) + "/"  + (BUILD_MAP) + "_parts_contourlines_gmapsupp.img")    
  if ExitCode != 0:
    if (BUILD_MAP) != "germany":
      ExitCode = os.system("test -d hoehenlinien/" + (BUILD_MAP))
      if ExitCode == 0:
        os.system("cp " + (work_dir) + "hoehenlinien/" + (BUILD_MAP) + "/gmapsupp.img " + (work_dir) + "gps_ready/unzipped/" + (BUILD_MAP) + "/" + (day) + "/"  + (BUILD_MAP) + "_parts_contourlines_gmapsupp.img")
    elif (BUILD_MAP) == "germany":
      os.system("cp " + (work_dir) + "gcontourlines/gmapsupp.img " + (work_dir) + "gps_ready/unzipped/" + (BUILD_MAP) + "/" + (day) + "/"  + (BUILD_MAP) + "_parts_contourlines_gmapsupp.img")   

def zip_file():
  os.chdir(work_dir) 
  os.chdir(dir2)
  print(os.getcwd())
  os.system("for file in *.img; do zip $file.zip $file; done")
  os.system("mv *.zip " + (work_dir) + (dir1))
  

if (MAP_TYPE) == "velomap":
  mk_store()
  velomap()
  merge()
  zip_file()
    
elif (MAP_TYPE) == "basemap":
  mk_store()
  basemap()
  merge()
  zip_file()
    
elif (MAP_TYPE) == "all":
  mk_store()  
  velomap()
  basemap()
  merge_all()
  copy_parts()
  zip_file()

printinfo("Habe fertig!")

""" 
## ToDo:

upload to local FTP-Server

## Changelog:

v0.9.3- separated folder for the maps per day

v0.9.2- addr- and boundary-layer added

v0.9.1- zip-function added

v0.9.0- all=parts+base+velo

## 2011-05-01 Projectstatus changed to RC

v0.8.5- minor fixes

v0.8.4- mkgmap.jar >> mkgmap_velo.jar for the velomap, style-copyright by Felix Hartmann

v0.8.3- add contourlines to gps_parts if available

v0.8.2- code cleanup, dirs added gps_parts and gps_ready

v0.8.1- separate Images for 'all' 

v0.8.0- AIO-basemap as additional maptype

## 2011-02-14 Projectstatus changed to BETA

v0.7.1- minor fixes

v0.7.0- download *.pbf (osmosis) or *.bz2, check osbsql2osm to use OSB-database-dumps

v0.6.8- Cleanups

v0.6.7- change work_dir to map_build

v0.6.6- better map-description, if more then one map is used on the GPS-device


v0.6.1- first working version with python3, but there are a lot of things to do,
        next is make it use startoptions and the pygmap.conf to remember these options
        there are many systemcalls, which only work on Linux, they must be changed
        removed many comments and code from the bash, because they make it unreadable

v0.6.0 - Beginn der Umstellung auf python, aktuell noch nicht benutzbar

"""