#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "0.6.1"
__author__ = "Bernd Weigelt, Jonas Stein"
__copyright__ = "Copyright 2010, The OSM-TroLUG-Project"
__credits__ = "Dschuwa"
__license__ = "GPL"
__maintainer__ = "Bernd Weigelt, Jonas Stein"
__email__ = "weigelt.bernd@web.de"
__status__ = "preAlpha"

""" 
  ===========VORSICHT ALPHA-STADIUM=================
  pygmap3.py, das script um ein gmapsupp.img für GARMIN-Navigationsgeräte
  zu erzeugen, z.B. Garmin eTrex Vista Hcx
  Ein Gemeinschaftsprojekt von Bernd Weigelt und Jonas Stein
  und als QCO Dschuwa

  License GPL
  
  Work in progress, bitte beachten!
  Prinzipiell funktioniert es, aber wenn was kaputt geht, 
  lehnen wir jegliche Haftung ab.
  
  
  Folgende Software wird benutzt:
  
  mkgmap von 
  http://wiki.openstreetmap.org/wiki/Mkgmap
  http://www.mkgmap.org.uk/snapshots/mkgmap-latest.tar.gz
 
  gmaptool von
  http://www.anpo.republika.pl/download.html
  gmt.exe
 
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
verbose = 1 ## nur zum Testen, default = 1 an dieser Stelle


work_dir = (os.environ['HOME'] + "/share/osm/map_build_test/") # Der letzte Slash muss sein!!!

RAMSIZE_DEFAULT = "-Xmx4000M"
MAXNODES_DEFAULT = "1000000"

BUILD_MAP_DEFAULT = "germany"



## Progamme und Verzeichnisse suchen

hint = ("mkdir " + (work_dir))
checkdir((work_dir), hint) 

hint = "Install: wine to work with gmt.exe from GMAPTOOLS"
checkprg("wine", hint)
 
hint = " Download: http://www.anpo.republika.pl/download.html "
checkprg("gmt.exe", hint)
 
hint = "Download:  http://tuxcode.org/john/osbsql2osm/osbsql2osm-latest.tar.gz"
checkprg("osbsql2osm", hint)

hint = " git fehlt, wird gebraucht um die mkgmap-Styles zu holen! "
checkprg("git", hint)

os.chdir(work_dir)


""" 
  Eigene Einstellungen werden aus pygmap.conf gelesen

  Konfigurationsdatei pygmap.conf, um Konflikte mit der eventuell
  vorhandenen creategmap.conf des Bashscriptes zu vermeiden.
"""

#checkfile("pygmap.conf", os.system("touch pygmap.conf"))

 
 
"""
 
  Default (Vorschlag):
  velomap  mit Bugs und Fixmes


		creategmap3.py [-options]

		-v		interaktiv mit der Möglichkeit, Optionen zu ändern
		-base		Basemap erstellen
		-nm  		Keine Kartendaten holen
		-nb  		keine neuen Bugs holen
		-L		Log einschalten
		-l		Log ausschalten


		Standard ist der Bau einer Velomap für mehr Kontrast auf kleinen Displays."

"""



""" 
  Einstellungen beim ersten Lauf, bei RAMSIZE und MAXNODES besteht eine
  Abhängigkeit, die eventuell sogar überprüft werden sollte. 
  Erfahrungswerte sind vorhanden, weitere sollten ermittelt werden.
"""
# 
if  verbose == 1:
    print(""" 
		
		Abhängig vom vorhandenen RAM muß die Menge des Speichers 
		für Java eingestellt werden.
		Unter 1 GiB dürfte eine Kartenerstellung nicht möglich sein.
		Empfohlen werden mindestens 2 GiB RAM!
		
		Standard bei 2 GiB RAM ist die Vorgabe von "-Xmx2000M"
		
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
		4+GiB (-Xmx3000M) -->	1000000
		
    """)       
    print("                Vorgabewert: ", (MAXNODES_DEFAULT))
    MAXNODES = input("                Bitte Anzahl der gewünschten Nodes eingeben. ")
    
    if MAXNODES == "":
        MAXNODES = (MAXNODES_DEFAULT)

    print("                Wahl:        ", (MAXNODES))

    print(""" 
	  
	   
	        Bitte beachten!"
	        Erstellen von Karten für einzelne Bundesländer ist nicht möglich,
	        diese können über die AIO-Downloadseite gefunden werden.
	   
	  
	        Mögliche Länder finden Sie unter http://download.geofabrik.de/osm/europe/
	        bitte nur den Dateinamen ohne Endung.
	  
    """)
    print("                Vorgabewert: ", (BUILD_MAP_DEFAULT))
    BUILD_MAP = input("                Bitte die gewünschte Karte eingeben ")
    
    if BUILD_MAP == "":
        BUILD_MAP = (BUILD_MAP_DEFAULT)
    
    print("                Wahl:        ", BUILD_MAP)



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
  get the contourlines for Germany, if not present
  other countries could be found at openmtp.org
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
        os.system("wine ~/bin/gmt.exe -j -f 5,25 -m HOEHE -o ../gmapsupp.img Topo\ D\ SRTM/*.img")
        os.chdir("..")
        os.system("rm -Rf temp")
        os.chdir(work_dir)

""" 
  Styles-Vorlagen werden von GIT-Server der AIO-Karte geholt
  Aktualisierungen erfolgen automatisch
  Eine Rückfallebene wäre sinnvoll, da die AIO-Styles nicht immer in Ordnung sind
"""   
   
ExitCode = os.system("test -d aiostyles")
    
if ExitCode == 0:
    os.chdir("aiostyles")
    os.system("git pull")
    os.chdir(work_dir)

else:
    os.system("git clone git://github.com/aiomaster/aiostyles.git")
    os.chdir(work_dir)


## add your own styles in mystyles and change the path for mkgmap 

ExitCode = os.system("test -d mystyles")
    
if ExitCode == 0:    
    mapstyle = "mystyles"

else:
    mapstyle = "aiostyles"
    
 
print(mapstyle) 
 
""" 
  Das Dumpfile für die OpenStreetBugs wird geholt. 
  
"""  

os.system("wget -N http://openstreetbugs.schokokeks.org/dumps/osbdump_latest.sql.bz2")
os.system("bzcat osbdump_latest.sql.bz2 | osbsql2osm > OpenStreetBugs.osm")


#  Download der OSM-Kartendaten von der Geofabrik

os.system("wget -N http://download.geofabrik.de/osm/europe/" + (BUILD_MAP) + ".osm.bz2")

 
 
## Entpacken der Kartendaten, bei den Europadaten sind es über 50 GiB, es sollte also genug 
## freier Platz auf der Festplatte sein. Deutschland hat rund 10 GiB

ExitCode = os.system("test -f " + (BUILD_MAP) + ".osm")

if ExitCode == 0:
    os.remove((BUILD_MAP) + ".osm")


os.system("bunzip2 -k " + (BUILD_MAP) + ".osm.bz2")
 

##  Arbeitsverzeichnis für Splitter wird erstellt...
 
ExitCode = os.system("test -d tiles")

if ExitCode == 0:
    os.chdir("tiles")
    os.system("rm -Rf *")
    os.chdir(work_dir)
	  
else: 
    os.mkdir("tiles")
             
## Splitten der Kartendaten, damit mkgmap damit arbeiten kann

os.chdir("tiles")
os.system("java -ea " + (RAMSIZE) + " -jar " + (splitter) + " --mapid=63240023 --max-nodes=" + (MAXNODES) + " --cache=cache " + (work_dir) + (BUILD_MAP) + ".osm")
os.chdir(work_dir)

## Erstellen der Arbeitsverzeichnisse

for dir in ['gfixme', 'gosb', 'gvelomap', 'gbasemap', 'gaddr', 'gmaxspeed', 'gboundary']:
    ExitCode = os.system("test -d " + (dir))
    if ExitCode != 0:
      os.mkdir(dir)
      
""" 
  Erstellen der Bugs- und FIXME-Layer für beide Kartenvarianten, Velomap oder AIO
 

  Die Optionen für MKGMAP sind in externe Dateien ausgelagert

  GBASEMAPOPTIONS  =  -c basemap.conf
  NOBASEMAPOPTIONS =  -c fixme_buglayer.conf
  VELOMAPOPTIONS   =  -c velomap.conf

"""
os.system("rm -Rf gfixme/* gosb/* ")

os.chdir("gfixme")

print(os.getcwd())
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + (work_dir) + "fixme_buglayer.conf --style-file=" + (work_dir) + (mapstyle) + "/fixme_style --description='Fixme' --family-id=3 --product-id=33 --series-name='OSMDEFixme' --family-name=OSMFixme --mapname=63242023 --draw-priority=16 " + (work_dir) + "tiles/*.osm.gz " + (work_dir) + "aiostyles/fixme.TYP")

os.chdir((work_dir) + "/gosb")

print(os.getcwd())
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + (work_dir) + "fixme_buglayer.conf --style-file=" + (work_dir) + (mapstyle) + "/osb_style --description='OSB' --family-id=2323 --product-id=42 --series-name='OSMBugs' --family-name=OSMBugs --mapname=63243023 --draw-priority=20 " + (work_dir) + "OpenStreetBugs.osm " + (work_dir) + "aiostyles/osb.TYP")
os.chdir(work_dir)
 
 
## Erstellen des Velomap-Layers

os.system("rm -Rf gvelomap/* ") 

os.chdir("gvelomap")

print(os.getcwd())
os.system("java -ea " + (RAMSIZE) + " -jar " + (mkgmap) + " -c " + (work_dir) + "velomap.conf --style-file=" + (work_dir) + "aiostyles/velomap_style " + (work_dir) + "tiles/*.osm.gz " + (work_dir) + "aiostyles/velomap.TYP")

os.chdir(work_dir)
 
 
## Optionen für die Basemap, bitte stehenlassen, werden noch gebraucht

#		  java -ea $RAMSIZE -jar $mkgmap -c ../basemap.conf --style-file=../aiostyles/basemap_style --description='Openstreetmap' --family-id=4 --product-id=45 --series-name='OSMDEbasemap' --family-name=OSMBasemap --mapname=63240023 --draw-priority=10 $work_dir/tiles/*.osm.gz $work_dir/aiostyles/basemap.TYP

#		  java -ea $RAMSIZE -jar $mkgmap -c ../fixme_buglayer.conf --style-file=../aiostyles/addr_style --description='Adressen' --family-id=5 --product-id=40 --series-name='OSMDEAddr' --family-name=OSMAdressen --mapname=63244023 --draw-priority=18  $work_dir/tiles/*.osm.gz $work_dir/aiostyles/addr.TYP

#		  java -ea $RAMSIZE -jar $mkgmap -c ../fixme_buglayer.conf --style-file=../aiostyles/boundary_style --description='Grenzen' --family-id=6 --product-id=30 --series-name='OSMDEboundary' --family-name=OSMGrenzen  --mapname=63245023 --draw-priority=20 $work_dir/tiles/*.osm.gz $work_dir/aiostyles/boundary.TYP

#		  java -ea $RAMSIZE -jar $mkgmap -c ../fixme_buglayer.conf --style-file=../aiostyles/maxspeed_style--family-name=maxspeed --series-name="maxspeed" --family-id=84 --product-id=15 --series-name=OSMmaxspeed --family-name=OSMmaxspeed --mapname=63246023 --draw-priority=21 $work_dir/tiles/*.osm.gz $work_dir/aiostyles/maxspeed.TYP

 
## Zusammenfügen der Kartenteile

if (BUILD_MAP) == "germany":
    os.system("wine ~/bin/gmt.exe -jo gmapsupp.img gvelomap/gmapsupp.img gosb/gmapsupp.img gfixme/gmapsupp.img gcontourlines/gmapsupp.img")
elif (BUILD_MAP) != "germany":
    ExitCode = os.system("test -d hoehenlinien/" + (BUILD_MAP))
    if ExitCode == 0:
        os.system("wine ~/bin/gmt.exe -jo gmapsupp.img gvelomap/gmapsupp.img gosb/gmapsupp.img gfixme/gmapsupp.img hoehenlinien/" + (BUILD_MAP) + "/gmapsupp.img")
    else:
        os.system("wine ~/bin/gmt.exe -jo gmapsupp.img gvelomap/gmapsupp.img gosb/gmapsupp.img gfixme/gmapsupp.img")
        
os.system("cp gmapsupp.img " + (work_dir) + (BUILD_MAP) + "_gmapsupp.img")


printinfo("Habe fertig!")

""" 
 
## Changelog:

v0.6.1- first working version with python3, but there are a lot of things to do,
       next is make it use startoptions and the pygmap.conf to remember these options
       there are many systemcalls, which only work on Linux, they must be changed
       removed many comments and code from the bash, because they make it unreadable

v0.6.0 - Beginn der Umstellung auf python, aktuell noch nicht benutzbar

"""