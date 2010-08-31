#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = 0.60
__author__ = "Bernd Weigelt, Jonas Stein"
__copyright__ = "Copyright 2010, The OSM-TroLUG-Project"
__credits__ = "Dschuwa"
__license__ = "GPL"
__maintainer__ = "Bernd Weigelt, Jonas Stein"
__email__ = "weigelt.bernd@web.de"
__status__ = "preAlpha"


import sys
import os
from http.client import *
import re

 
""" 
  ===========VORSICHT ALPHA-STADIUM=================
  creategmap.py, das script um ein gmapsupp.img für GARMIN-Navigationsgeräte
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
    
def getmkgmap(url):
    target = HTTPConnection(url)
    target.request('GET', 'http://www.mkgmap.org.uk/snapshots/')
    
    htmlcontent =  target.getresponse().read()

    pattern = re.compile('mkgmap-r\d{4}')
    LatestFile = sorted(pattern.findall(htmlcontent), reverse=True)[1]

    return LatestFile
    
def getsplitter(url):
    target = HTTPConnection(url)
    target.request('GET', 'http://www.mkgmap.org.uk/splitter/')
    
    htmlcontent =  target.getresponse().read()

    pattern = re.compile('splitter-r\d{3}')
    LatestFile = sorted(pattern.findall(htmlcontent), reverse=True)[1]

    return LatestFile
    
    
# VARs =============================================================================

web_help = "http://wiki.openstreetmap.org/wiki/User:Berndw"


"""
  Brauchen wir den eigentlich wirklich? 
  Bernd: Glaube ich nicht, höchstens für das Debuggen
"""  
FailCounter = 0

"""
  Diese Funktion sollte bestehen bleiben, um entweder bei Erstbenutzung
  ausführliche Infos zu geben, und eventuell die Möglichkeit des Rücksetzen
  auf die Default-Einstellungen bei Fehlern zu bieten
"""
firstrun = 0 ## nur zum Testen, default = 1 an dieser Stelle

""" Arbeitsverzeichnis """

work_dir = '~/share/osm/map_build'


"""
  Logfunktion sollte eventuell erweitert werden zur besseren Fehlerbehebung
  Log-, bzw. verbosity-Level sollte einstellbar sein, zumindest variabel
"""  
## Log
log = 0
enable_log = 0
disable_log = 0

"""
  Splitter und Mkgmap werden automatisch geholt und installiert
  Optionen können verbessert oder entfernt werden.
"""
## Wo ist mkgmap
mkgmap = "mkgmap/mkgmap.jar"
 
## Splitter
splitter = "splitter/splitter.jar"

"""
  Folgende Optionen sollten bei 'firstrun = 1' und Resets der Einstellungen 
  gesondert abgefragt werden, 
  Hinweistexte multilingual, mit Hinweis auf das Wiki
"""  
## Für Java 
RAMSIZE = "-Xmx2000M"
MAXNODES = 500000

"""
  Idee similar zu 'firstrun = 1' könnte zusammen gefasst werden
  Oder gibt es was besseres?
"""  
## Interaktiver Modus
abfrage = 0

"""
  Diese Optionen sollte per Konfigurationsdatei variabel sein
"""
## Standardkarte
default_map = "germany"
 
## Velomap erstellen
basemap = 0

"""
  Eigentlich geht es nicht ohne die folgenden drei Optionen, aber 
  wenn kein Download gewünscht, dünne Leitung oder wg. Tests, sollte 
  es die Möglichkeit geben, Arbeitsschritte zu 
  überspringen, falls alle Bedingungen erfüllt sind.
"""
## Download der aktuellen Kartendaten
download = 1
 
## OpenStreetBugs holen
bugsholen = 1
 
## Tilesverzeichnis löschen
rm_tiles = 1

"""
  Diese Option ist eigentlich sinnfrei, denn wenn nicht alles Teile 
  vorhanden sind, klappt das ganze nicht und es gibt andere Fehlermeldungen
  Kann also entfallen
"""  
## Falls was fehlt
merge_error = "Zusammenfügen der Karte klappt nicht, da nicht alle Teile vorhanden sind!"


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
print(os.getcwd())

""" 
  Eigene Einstellungen werden aus cgmap_py.conf gelesen

  Konfiguraionsdatei umbenannt nach cgmap_py.conf um Konflikte mit der eventuell
  vorhandenen creategmap.conf des Bashscriptes zu vermeiden.
"""


# checkfile("cgmap_py.conf", os.system("touch cgmap_py.conf"))

#source $work_dir/creategmap.conf
 
 
"""
  Optionen beim Programmstart stechen die Vorgaben aus dem Script 
  oder der Konfigurationsdatei, sollten aber in der Konfiguration
  gespeichert werden.
  Aufrufe des Scripts ohne Optionen sollten , wenn sinnvoll, die 
  vorangegangenen übernehmen.
  Default (Vorschlag):
  velomap  mit Bugs und Fixmes, wie beim Bashscript
"""  
 
#while test $# -gt 0
#do
#	case $1 in
#	-h)
print("""
		creategmap [-options]

		-i		interaktiv mit der Möglichkeit, Optionen zu ändern
		-base		Basemap erstellen
		-nm  		Keine Kartendaten holen
		-nb  		keine neuen Bugs holen
		-L		Log einschalten
		-l		Log ausschalten


		Standard ist der Bau einer Velomap für mehr Kontrast auf kleinen Displays."
		
""")


#		exit
#	;;
 
#	-i)
#		firstrun=1
#	;;
 
#	-base)
		# AIO-Basiskarte erstellen
print(" Basemap - on ")
#		basemap=1
#	;;
# 
#	-nm)
		# do not download german.osm
print(" Download - off ")
#		download=0
#	;;
# 
#	-nb)
		#  using old openstreetmap bugs
print(" Bugsholen - off ")
#		bugsholen=0
#	;;
# 
#	-L)
print(" Log - on ")
#		enable_log=1
#	;;
#
#	-l)
print(" Log - off ")
#		disable_log=0
#	;;
# 
#	*)
print(" error: invalid argument $1 ")
#		exit
#	;;  
#	esac
#	shift
#done

"""
  Logfunktion sollte an die Möglichkeiten von python angepasst werden,
  firstrun = 1 sollte auf jeden Fall log = 1 mit verbose = 3 (alles) haben.
  andere nur noch auf Wunsch.
"""

#if [ $enable_log = 1 ] ; then
#	log=1
#elif [ $disable_log = 1 ] ; then
#	mv creategmap.conf creategmap.conf.sec
#	sed '/log/d' creategmap.conf.sec > creategmap.conf	
#	log=0
#fi
#
#if [ $log = 1 ] ; then
#	if [ -f cgm.log  ] ; then :
#	else touch cgm.log
#	fi
#
#	if [ -f creategmap.conf ] ; then
#		mv creategmap.conf creategmap.conf.sec
#		sed '/log/d' creategmap.conf.sec > creategmap.conf
#	fi
#	echo log=1 >> creategmap.conf
#fi 
# 



""" 
  Einstellungen beim ersten Lauf, bei RAMSIZE und MAXNODES besteht eine
  Abhängigkeit, die eventuell sogar überprüft werden sollte. 
  Erfahrungswerte sind vorhanden, weitere sollten ermittelt werden.
"""
# 
if  firstrun == 1:
    print(""" 
		
		Abhängig vom vorhandenen RAM muß die Menge des Speichers 
		für Java eingestellt werden.
		Unter 1 GiB dürfte eine Kartenerstellung nicht möglich sein.
		Empfohlen werden mindestens 2 GiB RAM!
		
		Standard bei 2 GiB RAM ist die Vorgabe von "-Xmx2000M"
		
    """)
    print("		Vorgabewert: ",RAMSIZE) 
    RAMSIZE = input("		Wieviel Speicher soll verwendet werden? ")
    print("		Wahl:        ",RAMSIZE)



#	  if  [ -z $RAMSIZE ] ; then 
#		  RAMSIZE=$RAMSIZE_OLD
#	  fi
#	  if [ -f creategmap.conf ] ; then
#	    mv creategmap.conf creategmap.conf.sec
#	    sed '/RAMSIZE/d' creategmap.conf.sec > creategmap.conf
#	  fi
#	  echo RAMSIZE=$RAMSIZE >> creategmap.conf

 
if  firstrun == 1:
    print(""" 
		
		Bei kleineren Karten können die Werte für die MAXNODES bei Splitter eventuell 
		heraufgesetzt werden, große Karten wie Deutschland und Frankreich sollten mit 
		den folgenden Vorschlagswerten erstellt werden.

		2 GiB (-Xmx2000M) -->	 500000
		4+GiB (-Xmx3000M) -->	1000000
		
    """)       
    print("		Vorgabewert: ",MAXNODES)
    MAXNODES = input("		Bitte Anzahl der gewünschten Nodes eingeben. ")
    print("		Wahl:        ",MAXNODES)


#	  if  [ -z $MAXNODES ] ; then 
#		  MAXNODES=$MAXNODES_OLD
#	  fi
#	  if [ -f creategmap.conf ] ; then
#	    mv creategmap.conf creategmap.conf.sec
#	    sed '/MAXNODES/d' creategmap.conf.sec > creategmap.conf
#	  fi
#	  echo MAXNODES=$MAXNODES >> creategmap.conf

#fi


"""
  Wenn möglich sollte auch der Bau der kleineren Karten möglich sein.
  Wäre eine Suchfunktion sinnvoll?
  Oder eine Auswahl anhand von directory-listings?
  Oder wäre das etwas für eine spätere grafische Version?
"""

#if [ $firstrun -eq 1 ] ; then
#    map= 
#    while [ -z $map ] ; do
if  firstrun == 1:
    print(""" 
	  
	   
	        Bitte beachten!"
	        Erstellen von Karten für einzelne Bundesländer ist nicht möglich,
	        diese können über die AIO-Downloadseite gefunden werden.
	   
	  
	        Mögliche Länder finden Sie unter http://download.geofabrik.de/osm/europe/
	        bitte nur den dateinamen ohne Endung.
	  
	        Wahl wird in creategmap.conf gespeichert, zum Ändern die Option "-i" 
	        beim Aufruf des Scriptes verwenden. "
	   
	        europe erzeugt eine Europa-Karte, bitte nur bei ausreichend RAM! 
                Und dieser Vorgang dauert sehr lang und gelingt nicht unbedingt immer.
       	  
    """)
    print("		Vorgabewert: ",default_map)
    map = input("		Bitte die gewünschte Karte eingeben ")
    print("		Wahl:        ",map)
#	  echo -n "       Ländernamen (englisch) ohne Dateiendung eingeben " [$default_map]
#	  read map
#	  if  [ -z $map ] ; then 
#		  map=$default_map
#	  fi
#	  if [ -f creategmap.conf ] ; then
#	    mv creategmap.conf creategmap.conf.sec
#	    sed '/map/d' creategmap.conf.sec > creategmap.conf
#	  fi
#	  echo map=$map >> creategmap.conf
#     done
#fi

"""
  Einstellungen, die geändert werden sollten auf jeden fall ins Log
"""  
#if [ $log = 1 ] ; then
#	time=`date '+%Y.%m.%d_%H:%M'`
#	echo $time" cgm-version: " $version "   " $mkr "   " $spr "   " $map "   " $RAMSIZE "   " $MAXNODES >> cgm.log
#fi 

""" 
  Holen der Sachen von mkgmap.org
  Bash-Funktionen nur als Hinweis
"""
#print(("http://www.mkgmap.org.uk/snapshots/%s.tar.gz") %getmkgmap("www.mkgmap.org.uk"))

#tar -xvzf mkgmap-%s.tar.gz
#ln -s mkgmap-%s mkgmap

#print(("http://www.mkgmap.org.uk/splitter/%s.tar.gz") %getsplitter("www.mkgmap.org.uk"))

#tar -xvzf splitter-%s.tar.gz
#ln -s splitter-%s splitter

"""
  Diese Funktion ist für mich wichtig, könnte aber in einem separaten Modul versteckt werden
  Oder vorhandene eigene Änderungen haben eine höhere Priorität, dann braucht man die MKGMAP-Optionen
  nicht zu verändern. Voraussetzung wäre aber ein separates Verzeichnis mit dem eigenen Styles.
  Sollte im Log berücksichtigt werden.
"""  
 
## auf meinem Rechner benutze ich eine alternative Einstellung für die Darstellung von Bugs und Fixmes
## Erläuterungen finden sich auf der AIO-Wiki-Seite
 
#if [ -d mystyles ] ; then
#      mapstyles=mystyles
#else
#      mapstyles=aiostyles
#fi
 
""" 
  Styles-Vorlagen werden von GIT-Server der AIO-Karte geholt
  Aktualisierungen erfolgen automatisch
  Eine Rückfallebene wäre sinnvoll, da die AIO-Styles nicht immer in Ordnung sind
"""  
 
#if [ -d aiostyles ] ; then 
#	   cd aiostyles
#	   git pull
#	   cd ..
#else	  
#	  mkdir aiostyles
#	  $git clone git://github.com/aiomaster/aiostyles.git
#fi
 
#if [ -d aiostyles ] ; then :
#else 
#	      print(" Styles nicht gefunden! '
#	      echo $web_help 
#	      exit
#fi
 
""" 
  Arbeitsverzeichnis für Splitter wird erstellt...
"""
 
#if [ -d tiles ] ; then :
#else mkdir tiles
#fi
 
"""  
  und, falls alte Daten vorhanden,geleert
"""

#if [ $rm_tiles -eq 1 ] ; then 
#	tiles_dir='tiles'
#	for i in $tiles_dir; do 
#	cd $i
#	rm -Rf *
#	cd ..
#	done
#fi
 
 
""" 
  Die Höhenlinien werden einmalig geholt, hier nur für Deutschland, andere z.Z. nur manuell, 
  siehe Änderung v0.50.
  Es gibt weitere bei openmtpmap.org, diese könnte man in irgendeiner Form vorbereitet (ready2use)
  zur Verfügung stellen. Dafür wäre aber Webspace erforderlich.
"""


#if [ -f gcontourlines/gmapsupp.img ] ; then :
#else 

printinfo("Hole die benötigten Höhenlinien!")

#	if [ -d gcontourlines ] ; then : 
#	else mkdir gcontourlines
#	fi
#	cd gcontourlines
#	rm -Rf *
#	mkdir temp
#	cd temp
#	wget -N http://www.glade-web.de/GLADE_geocaching/maps/TOPO_D_SRTM.zip
#	unzip Topo_D_SRTM.zip
#	$wine ../../gmt/gmt.exe -j -f 5,25 -m HOEHE -o ../gmapsupp.img Topo\ D\ SRTM/*.img
#	cd ..
#	rm -R temp
#	cd ..
#fi
 
""" 
  Das Dumpfile für die OpenStreetBugs wird geholt. 
  Eine direkte Abfrage des OSB-Server ist möglich, ich habe da noch ein perlscript rum liegen,
  aber ob das nötig ist?
"""  
 
#if [ $bugsholen -eq 1 -o ! -f osbdump_latest.sql.bz2 ] ; then
#	if [ -f osbdump_latest.sql.bz2 ] ; then
#		rm osbdump*
#	fi
#	wget -N http://openstreetbugs.schokokeks.org/dumps/osbdump_latest.sql.bz2
#	## Umwandlung der Bugs ins OSM-Format
#	bzcat osbdump_latest.sql.bz2 | $osbsql2osm > OpenStreetBugs.osm
#fi
 
"""
  Download der OSM-Kartendaten von der Geofabrik
"""  
 
#if [ $download -eq 1 ] ; then
#	if [ $map = europe ] ; then
#	    wget -N http://download.geofabrik.de/osm/europe.osm.bz2
#	else  
#	    wget -N http://download.geofabrik.de/osm/europe/$map.osm.bz2
#	fi
#fi
 
 
## Entpacken der Kartendaten, bei den Europadaten sind es über 50 GiB, es sollte also genug 
## freier Platz auf der Festplatte sein. Deutschland hat rund 10 GiB
 
#if [ -f $map.osm.bz2 ] ; then
#	if [ -f $map.osm ] ; then
#	    rm $map.osm
#	fi
#	bunzip2 -k $map.osm.bz2
#else	echo "$map.osm.bz2 nicht gefunden..."  ; exit
#fi
 
 
## Splitten der Kartendaten, damit mkgmap damit arbeiten kann
 
#if [ $rm_tiles -eq 1 ] ; then
#	cd tiles
#	java -ea $RAMSIZE -jar $splitter --mapid=63240023 --max-nodes=$MAXNODES --cache=cache ../$map.osm
#	cd ..
#fi
 
""" 
  Die Optionen für MKGMAP sind in externe Dateien ausgelagert

  GBASEMAPOPTIONS =  -c basemap.conf
  NOBASEMAPOPTIONS = -c fixme_buglayer.conf
  VELOMAPOPTIONS = -c velomap.conf
"""

## Erstellen der Bugs- und FIXME-Layer für beide Kartenvarianten, Velomap oder AIO
 
#dirs="gfixme gosb "
#	for i in $work_dirs; do
#	  if [ -d $i ] ; then
#	    cd $i  
#	    rm -Rf *
#	    cd ..
#	  else mkdir $i
#	  fi
#	done
 
#	echo $mapstyles 
 
#	  cd gfixme
#		  echo $PWD
#		  java -ea $RAMSIZE -jar $mkgmap -c ../fixme_buglayer.conf --style-file=../$mapstyles/fixme_style --description='Fixme' --family-id=3 --product-id=33 --series-name='OSMDEFixme' --family-name=OSMFixme --mapname=63242023 --draw-priority=23 $work_dir/tiles/*.osm.gz $work_dir/$mapstyles/fixme.TYP
#	  cd ../gosb
#		  echo $PWD
#		  java -ea $RAMSIZE -jar $mkgmap -c ../fixme_buglayer.conf --style-file=../$mapstyles/osb_style --description='OSB' --family-id=2323 --product-id=42 --series-name='OSMBugs' --family-name=OSMBugs --mapname=63243023 --draw-priority=22 $work_dir/OpenStreetBugs.osm $work_dir/$mapstyles/osb.TYP
#	  cd ../
 
 
## Erstellen des Velomap-Layers
 
#if [ $basemap -eq 0 ] ; then
#	  dirs_velomap="gvelomap"
#	  for i in $work_dirs_velomap; do
#	    if [ -d $i ] ; then
#	      cd $i  
#	      rm -Rf *
#	      cd ..
#	    else mkdir $i
#	    fi
#	  done
#	  cd gvelomap
#		  echo $PWD
#		  java -ea $RAMSIZE -jar $mkgmap -c ../velomap.conf --style-file=../aiostyles/velomap_style --description='Velomap' --family-id=6365 --product-id=1 --series-name='OSMDEVelomap' --family-name=OSMVelomap --mapname=63240023 --draw-priority=10 $work_dir/tiles/*.osm.gz $work_dir/aiostyles/velomap.TYP
#	  cd ../
 
 
## oder der AIO-Karte, diese enthält zusätzlich einen Adress-, einen Grenz- und einen Maxspeed-Layer, jeweils abschaltbar im Kartenmenü des Navis.	  
 
#elif [ $basemap -eq 1 ] ; then
#	dirs_basemap="gbasemap gaddr gboundary gmaxspeed"
#	  for i in $work_dirs_basemap; do
#	    if [ -d $i ] ; then
#	      cd $i  
#	      rm -Rf *
#	      cd ..
#	    else mkdir $i
#	    fi
#	  done
#	  cd gbasemap
#		  echo $PWD
#		  java -ea $RAMSIZE -jar $mkgmap -c ../basemap.conf --style-file=../aiostyles/basemap_style --description='Openstreetmap' --family-id=4 --product-id=45 --series-name='OSMDEbasemap' --family-name=OSMBasemap --mapname=63240023 --draw-priority=10 $work_dir/tiles/*.osm.gz $work_dir/aiostyles/basemap.TYP
#	  cd ../gaddr
#		  echo $PWD
#		  java -ea $RAMSIZE -jar $mkgmap -c ../fixme_buglayer.conf --style-file=../aiostyles/addr_style --description='Adressen' --family-id=5 --product-id=40 --series-name='OSMDEAddr' --family-name=OSMAdressen --mapname=63244023 --draw-priority=18  $work_dir/tiles/*.osm.gz $work_dir/aiostyles/addr.TYP
#	  cd ../gboundary
#		  echo $PWD
#		  java -ea $RAMSIZE -jar $mkgmap -c ../fixme_buglayer.conf --style-file=../aiostyles/boundary_style --description='Grenzen' --family-id=6 --product-id=30 --series-name='OSMDEboundary' --family-name=OSMGrenzen  --mapname=63245023 --draw-priority=20 $work_dir/tiles/*.osm.gz $work_dir/aiostyles/boundary.TYP
#	  cd ../gmaxspeed
#		  echo $PWD
#		  java -ea $RAMSIZE -jar $mkgmap -c ../fixme_buglayer.conf --style-file=../aiostyles/maxspeed_style--family-name=maxspeed --series-name="maxspeed" --family-id=84 --product-id=15 --series-name=OSMmaxspeed --family-name=OSMmaxspeed --mapname=63246023 --draw-priority=21 $work_dir/tiles/*.osm.gz $work_dir/aiostyles/maxspeed.TYP
#	  cd ../  
#fi
 
 
## Zusammenfügen der Kartenteile
 
#if [ -f gvelomap/gmapsupp.img -a -f gosb/gmapsupp.img -a -f gfixme/gmapsupp.img -a $basemap -eq 0 ] ; then
#	$wine $work_dir/gmt/gmt.exe -jo gmapsupp.img gvelomap/gmapsupp.img gosb/gmapsupp.img gfixme/gmapsupp.img
#elif [ -f gbasemap/gmapsupp.img -a -f gosb/gmapsupp.img -a -f gaddr/gmapsupp.img -a -f gfixme/gmapsupp.img -a -f gboundary/gmapsupp.img -a -f gmaxspeed/gmapsupp.img -a $basemap -eq 1 ] ; then
#	$wine $work_dir/gmt/gmt.exe -jo gmapsupp.img gbasemap/gmapsupp.img gosb/gmapsupp.img gaddr/gmapsupp.img gfixme/gmapsupp.img gboundary/gmapsupp.img gmaxspeed/gmapsupp.img
#else echo $merge_error ; exit
#fi
 
 
## Für einige Länder gibt es Höhenlinien
 
#if [ $map = germany ] ; then 
#	mv gmapsupp.img flat_gmapsupp.img
#	$wine $work_dir/gmt/gmt.exe -jo gmapsupp.img gcontourlines/gmapsupp.img flat_gmapsupp.img
#elif [ -d hoehenlinien/$map ] ; then
#	mv gmapsupp.img flat_gmapsupp.img
#	$wine $work_dir/gmt/gmt.exe -jo gmapsupp.img hoehenlinien/$map/gmapsupp.img flat_gmapsupp.img
#fi
 
#if [ -f flat_gmapsupp.img ] ; then
#	rm flat_gmapsupp.img
#fi
 
"""
  Nach Erstellen einer(mehrere?) Sicherungen
  kopieren der fertigen Karte ins Oberhaus mit aussagekräftigen Namen.
""" 

#cp gmapsupp.img ../$map.gmapsupp.img
 
 
## Aufräumen
 
#rm -f $map.osm
 
 
## Wenn wir bis hier gekommen sind, firstrun=0 und Leerzeilen entfernen
 
#mv creategmap.conf creategmap.conf.sec
#sed '/firstrun/d;/^ *$/d' creategmap.conf.sec > creategmap.conf
#echo firstrun=0 >> creategmap.conf
#rm creategmap.conf.sec


printinfo("Habe fertig!")

 
 
## Änderungen:
# v0.6.0a1 - Beginn der Umstellung auf python, aktuell noch nicht benutzbar

# v0.53- Erste Änderungen während der Betaphase, Texte und Grundeinstellungen
#	 Logfunktion implentiert

# v0.52- Anpassung an die Dokumentation von Dschuwa
 
# v0.51- CleanUps
 
# v0.50- Höhenlinien für einige Länder, die Daten gibt es bei http://openmtbmap.org/de/download/#hoehendaten
#        Die Rohdaten müssen mit gmt.exe zu gmapsupp.img zusammengefügt, Anleitung liegt jeweils bei.
#        Fertige gmapsupp.img sollten unter $work_dir/hoehenlinien/$map gespeichert werden, damit
#        das Script sie findet.
#
#        Mit wine kann man das mit folgender Zeile erledigen, gmt.exe liegt dabei im Verzeichnis darüber:
#       'wine ../gmt.exe  -j -f 5,25 -m HOEHE -o gmapsupp.img  *.img' 
#       'wine gmt.exe -jo gmapsupp.img */gmapsupp.img' erstellt eine große Datei (660 MiB) für alle Länder
#        kann man für die Europakarte verwenden, die ganze Karte wird etwa 4,8 GiB groß ;-)
#
 
 
# v0.49- Fehlerkorrekturen
 
# v0.47- firstrun = interaktiv
 
# v0.46- firstrun-Funktion für Grundeinstellungen
