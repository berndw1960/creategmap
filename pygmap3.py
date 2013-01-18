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
__version__ = "0.9.44"
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
import datetime
import argparse
import configparser
import time


# own modules

import clean_up
import splitter_mkgmap
import fetch
import contourlines


"""
  argparse
  
"""

parser = argparse.ArgumentParser(
        prog='PROG', 
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\
        
            Zum Bauen diverser Karten für Garmin PNA
            
            AIO-Basemap (eingebaut)
            AIO-FIXME (eingebaut)
            RadReiseKarte by Aighes (möglich)
            Contourlines (möglich)
            
            Das Copyright der Styles liegt bei den jeweiligen Autoren!
            The AIO-Style is Public Domain
            The RRK-Style is CC-BY 2.0 --> http://www.aighes.de/OSM/index.php
             
            Eigene poly-Dateien können im Verzeichnis 'poly' im 
            Arbeitsverzeichnis abgelegt werden. 
            Der Namen muss identisch zur Karte sein mit der Endung '.poly'
                          
            Hamburg     --> -b hamburg  
            Bayern      --> -b bayern
            Deutschland --> -b germany
            D_A_CH      --> -b dach (default)
            Europa      --> -b europe (nicht nutzbar wegen FAT, zu groß!)   

            Spezielle Einstellungen können in der 'pygmap3.cfg' gemacht werden.
            
            
        '''))

parser.add_argument('-b', '--buildmap', dest='buildmap', default='dach')
args = parser.parse_args()

WORK_DIR = (os.environ['HOME'] + "/map_build/")

# Der letzte Slash muss sein!!!


"""
  needed programs und dirs
  
"""

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
    


hint = "osmconvert missed, needed to cut data from the planet.o5m"
checkprg("osmconvert", hint)

hint = "Install: 7z to extract mkgmap's stylefiles"
checkprg("7z", hint)

os.chdir(WORK_DIR)

ExitCode = os.path.exists((WORK_DIR) + "pygmap3.lck")
if ExitCode == True:
  printerror(" There's another instance of pygmap3.py running...")

datei = open((WORK_DIR) + "pygmap3.lck", "w")
datei.close()   

hint = "get the bounds-*.zip from navmaps.eu and rename it to bounds.zip"
is_there("bounds.zip", hint)

hint = "RRK-Style missed, get it from www.aighes.de"
is_there("mystyles/rrk_typ.txt", hint)

hint = ("No Planet-File found! ")
is_there("planet.o5m", hint)

ExitCode = os.path.exists("fixme_buglayer.conf")
if ExitCode == True:
  printerror(" Please rename 'fixme_buglayer.conf' to 'fixme.conf'")
  quit()
  

"""
  configparser

"""  
def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)
    
config = configparser.ConfigParser()
ExitCode = os.path.exists((WORK_DIR) + "pygmap3.cfg")
if ExitCode == False:
  config['DEFAULT'] = {'ramsize': '-Xmx3G',
                       'mapid': '6324', 
                       'zip_img': 'yes',
                       'buildmap': 'dach',}
  
  config['splitter'] = {}
  config['splitter'] = {'version': 'latest', 
                        'maxnodes': '1200000',}
  
  config['mkgmap'] = {}
  config['mkgmap'] = {'version': 'latest'}
  
  config['basemap'] = {}
  config['basemap'] = {'build': 'yes',
                       'conf': 'map.conf',
                       'family-id': '4', 
                       'product-id': '45', 
                       'family-name': 'AIO-Basemap', 
                       'draw-priority': '10', 
                       'mapid_ext': '1001',}
                       
  config['rrk'] = {}
  config['rrk'] = {'build': 'no',
                   'conf': 'map.conf',
                   'family-id': '1', 
                   'product-id': '1000', 
                   'family-name': 'RadReiseKarte', 
                   'draw-priority': '12', 
                   'mapid_ext': '2001',}
                   
  config['fixme'] = {}
  config['fixme'] = {'build': 'yes', 
                       'conf': 'fixme.conf',
                       'family-id': '3', 
                       'product-id': '33', 
                       'family-name': 'OSM-Fixme', 
                       'draw-priority': '16', 
                       'mapid_ext': '6001',}
                       
  config['contourlines'] = {}
  config['contourlines'] = {'build': 'no'}
  write_config()


config.read('pygmap3.cfg')

if ('runtime' in config) == True:
  config.remove_section('runtime')
  write_config()
   
config.add_section('runtime')

""" 
  set buildmap
  
"""

config.set('runtime', 'buildmap', (args.buildmap))

write_config()
buildmap = config.get('runtime', 'buildmap')



"""
  set buildday for info in PNA

"""  

today = datetime.datetime.now()
DAY = today.strftime('%Y_%m_%d')
buildday = ((buildmap) + "/" + (DAY))

config.set('runtime', 'buildday', (buildday))

write_config()
buildday = config.get('runtime', 'buildday')

config.read('pygmap3.cfg')
print(buildday)

time.sleep(5)



"""
  dirs generate or remove old files
  
"""
         
clean_up.clean_build_dirs()


"""
  create dir for areas. poly and splitter-output
  
"""  
for dir in ['o5m', 'areas', 'poly', 'contourlines', 'tiles']: 
  ExitCode = os.path.exists(dir)
  if ExitCode == False:
   os.mkdir(dir)


"""
  get splitter and mkgmap 
  
"""  
splitter_mkgmap.get_tools()



"""
  get the geonames for splitter
  
"""

ExitCode = os.path.exists("cities15000.zip")
if ExitCode == False:
  os.system("wget http://download.geonames.org/export/dump/cities15000.zip")




"""
is there a keep_data.lck, then use the old data

"""

BUILD_O5M = ((WORK_DIR) + "o5m/" + (buildmap) + ".o5m")  
ExitCode = os.path.exists("keep_data.lck")
if ExitCode == False:
  printinfo("keep_data switched off!")
  fetch.fetch()
else:
  printwarning("keep_data switched on!")
  ExitCode = os.path.exists(BUILD_O5M)
  if ExitCode == False:
    fetch.fetch()
    
os.chdir(WORK_DIR)



 
"""
  split rawdata
  
"""

ExitCode = os.path.exists((WORK_DIR) + "no_split.lck")
if ExitCode == False:
  path = 'tiles'
  for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
      try:
        os.remove(os.path.join(path, file))
      except: 
        print('Could not delete', file, 'in', path)
  splitter_mkgmap.split()
  
elif ExitCode == True:
  ExitCode = os.path.exists((WORK_DIR) + "tiles/" + (buildmap) + "_split.ready")
  if ExitCode == False:
    path = 'tiles'
    for file in os.listdir(path):
      if os.path.isfile(os.path.join(path, file)):
        try:
          os.remove(os.path.join(path, file))
        except:
          print('Could not delete', file, 'in', path)
    splitter_mkgmap.split()
    
    
    
os.chdir(WORK_DIR)


"""
  make the dirs to store the images

"""  

zip_dir = ((WORK_DIR) + "gps_ready/zipped/" + (buildday) + "/")
unzip_dir = ((WORK_DIR) + "gps_ready/unzipped/" + (buildday) + "/")

cl_dir = ((WORK_DIR) + "contourlines/" + (buildmap) + "/")
cltemp_dir = ((WORK_DIR) + "contourlines/temp/")

for dir in [(zip_dir), (unzip_dir), (cltemp_dir)]:
  ExitCode = os.path.exists(dir)
  if ExitCode == True:
    path = (dir) 
    for file in os.listdir(path):
      if os.path.isfile(os.path.join(path, file)):
        try:
          os.remove(os.path.join(path, file))
        except:
          print('Could not delete', file, 'in', path)
            
  elif ExitCode == False:
    os.makedirs(dir)

ExitCode = os.path.exists(cl_dir)
if ExitCode == False:
  os.makedirs(cl_dir)
  
splitter_mkgmap.mkgmap_render()

os.chdir(WORK_DIR)


"""
  rename the images

"""  
  
os.chdir(WORK_DIR)
  
build = (config.get('contourlines', 'build'))
if build == "yes":
  contourlines.create_cont()

"""
 copy *kml to zipped-dirs
 
"""
  
os.chdir(WORK_DIR)

           
ExitCode = os.path.exists("tiles/" + (buildmap) + ".kml")
if ExitCode == True: 
  os.system("mv tiles/" + (buildmap) + ".kml " + (zip_dir)) 
"""
  zipp the images and mv them to separate dirs

"""
zip_img = (config.get('DEFAULT', 'zip_img'))
if zip_img == "yes":  
  os.chdir(unzip_dir)
  os.system("for file in *.img; do zip $file.zip $file; done")
  os.system("mv *.zip " + (zip_dir))


config.remove_section('runtime')

os.remove((WORK_DIR) + "pygmap3.lck")
printinfo("Habe fertig!")
quit()

""" 

## Changelog:
v0.9.44 - first steps for configparser

v0.9.43 - download from geofabrik removed

v0.9.42 - create contourlines if needed

v0.9.41 - dir for splitter-output

v0.9.40 - more python, removed 'test -[f|d]'

v0.9.38 - mkgmap.org, sitestructure is changed

v0.9.37 - use *.o5m as input for splitter

v0.9.36 - simplify workprocess

v0.9.35 - some changes in workprocess
          some changes at mkgmap-options


"""

