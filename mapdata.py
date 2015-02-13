#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
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
  buildmap = config.get('runtime', 'buildmap')
  BUILD_TEMP = ("o5m/" + (buildmap) + ".temp.o5m")
  BUILD_O5M = ("o5m/" + (buildmap) + ".o5m")
  BUILD_OLD = ("o5m/" + (buildmap) + ".old")

  if os.path.exists("o5m/planet.o5m") == True:
    print()
    printinfo("now extracting " + (buildmap) + ".o5m from Planet, please wait...")
    os.system("osmconvert o5m/planet.o5m " +
              "--complete-ways --complex-ways --drop-version " +
              " -B=poly/" + (buildmap) + ".poly " +
              " -o=" + (BUILD_TEMP))

    if os.path.exists(BUILD_O5M) == True:
      os.rename((BUILD_O5M), (BUILD_OLD))

    os.rename((BUILD_TEMP), (BUILD_O5M))

    if os.path.exists(BUILD_OLD) == True:
      os.remove(BUILD_OLD)
  else:
    print()
    printerror((WORK_DIR) + "o5m/planet.o5m not found... ")
    print("please download it with 'planet_up.py'")
    print()
    quit()

def update_o5m():
  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')

  print()
  printinfo("updating " + (buildmap) + ".o5m, please wait...")
  os.system("osmupdate --daily --hourly -B=poly/" + (buildmap) +
	    ".poly --keep-tempfiles o5m/" + (buildmap) +
	    ".o5m  o5m/" + (buildmap) +  "_new.o5m")

  os.chdir("o5m")

  if os.path.exists((buildmap) +  "_new.o5m") == True:
    os.rename((buildmap) + ".o5m", (buildmap) + "_temp.o5m")
    os.rename((buildmap) + "_new.o5m", (buildmap) + ".o5m")
    if os.path.exists((buildmap) + ".o5m") == True:
      os.remove((buildmap) + "_temp.o5m")

  os.chdir(WORK_DIR)

  if config.has_section('time_stamp') == False:
    config.add_section('time_stamp')
    write_config()

  today = datetime.datetime.now()
  DATE = today.strftime('%Y%m%d_%H00')

  config.set('time_stamp', (buildmap), (DATE))
  write_config()

