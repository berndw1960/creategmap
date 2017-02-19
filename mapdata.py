#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import datetime
import configparser

WORK_DIR = (os.environ['HOME'] + "/map_build/")

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)

"""
configparser

"""
def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

config = configparser.ConfigParser()


"""
cut data from planet-file

"""

def create_o5m():

  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')
  buildmap = config['runtime']['buildmap']
      
  if os.path.exists("o5m/" + buildmap + "osm.pbf") == True:
    print()
    printinfo("converting o5m/" + buildmap + ".osm.pbf to o5m/" + buildmap + ".o5m, please wait...")
    os.system("osmconvert o5m/" + buildmap + ".osm.pbf -o=o5m/" + buildmap + ".o5m")

  elif os.path.exists("o5m/" + buildmap + "-latest.osm.pbf") == True:
    print()
    printinfo("converting o5m/" + buildmap + "-latest.osm.pbf to o5m/" + buildmap + ".o5m, please wait...")
    os.system("osmconvert o5m/" + buildmap + "-latest.osm.pbf -o=o5m/" + buildmap + ".o5m") 
    
  elif os.path.exists("o5m/planet.o5m") == True:
    if config['runtime']['use_bbox'] == "yes":
      print()
      printinfo("now extracting " + buildmap + ".o5m from Planet, please wait...")
      os.system("osmconvert o5m/planet.o5m " +
              "--complete-ways --complex-ways --drop-version " +
              " -b=" + config['runtime']['bbox'] +
              " -o=o5m/" + buildmap + ".o5m")      
      
    elif os.path.exists("poly/" + buildmap + ".poly") == True:
      print()
      printinfo("now extracting " + buildmap + ".o5m from Planet, please wait...")
      os.system("osmconvert o5m/planet.o5m " +
              "--complete-ways --complex-ways --drop-version " +
              " -B=poly/" + buildmap + ".poly " +
              " -o=o5m/" + buildmap + ".o5m")
    else:
      print()
      printerror("missing poly/" + buildmap + ".poly")
      print()
      printinfo("created it or try to get one from http://download.geofabrik.de ")
      print("    or use another source for this file")
      print()
      quit()

  else:
    print()
    printerror((WORK_DIR) + "o5m/" + buildmap + ".o5m not found! ")
    print()
    printinfo("Solution 1 (should be preferred):")
    print()
    print("    Store one of the following files in " + WORK_DIR + "o5m ")
    print()
    print("    " + buildmap + "-latest.osm.pbf (from http://download.geofabrik.de) ")
    print("    " + buildmap + ".osm.pbf")    
    print("    " + buildmap + ".o5m")
    print()
    print("    it will be used the next time when you start pygmap3.py -b " + buildmap)  
    print()
    printinfo("Solution 2:")
    print()
    print("    If you have a " + buildmap + ".poly stored in " + WORK_DIR + "poly,")
    print("    then the missed " + buildmap + ".o5m can be extracted from a planet file by pygmap3.py. ") 
    print("    You can download the complete planet file wth planet_up.py,")
    print("    but the planet file has a size of more then 20 GiB, so it is the second best solution ")
    print("    If you had download this file, backup it and it can be updated with planet_up.py,too.")
    print()
    quit()

def update_o5m():

  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')
  buildmap = config['runtime']['buildmap']
  time = datetime.datetime.now()

  if config['runtime']['minutely'] == "yes":
    update_opts = " --hourly -- minutely "
    DATE = time.strftime('%Y%m%d_%H%M')  
    
  elif config['runtime']['hourly'] == "yes":
    update_opts = " --hourly "
    DATE = time.strftime('%Y%m%d_%H00')   
    
  else:
    update_opts = " "
    DATE = time.strftime('%Y%m%d_0000')
    
  print()
  printinfo("updating " + buildmap + ".o5m, please wait...")
  if config['runtime']['use_bbox'] == "yes":
    os.system("osmupdate --daily" + update_opts + 
        " -b=" + config['runtime']['bbox'] +
	    " --keep-tempfiles o5m/" + buildmap +
	    ".o5m  o5m/" + buildmap +  "_new.o5m")
  else:
    os.system("osmupdate --daily" + update_opts + 
        " -B=poly/" + buildmap +".poly "
	    " --keep-tempfiles o5m/" + buildmap +
	    ".o5m  o5m/" + buildmap +  "_new.o5m")

  os.chdir("o5m")

  if os.path.exists(buildmap +  "_new.o5m") == True:
    os.rename(buildmap + ".o5m", buildmap + "_temp.o5m")
    os.rename(buildmap + "_new.o5m", buildmap + ".o5m")
    if os.path.exists(buildmap + ".o5m") == True:
      os.remove(buildmap + "_temp.o5m")

  os.chdir(WORK_DIR)

  if config.has_section('time_stamp') == False:
    config.add_section('time_stamp')

  config.set('time_stamp', buildmap, DATE)

  write_config()
  
