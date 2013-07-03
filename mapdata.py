#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import datetime
import configparser


# defaults =============================================================================

work_dir = (os.environ['HOME'] + "/map_build/")


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
  os.chdir(work_dir)
  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')
  BUILD_TEMP = ("o5m/" + (buildmap) + ".temp.o5m")
  BUILD_O5M = ("o5m/" + (buildmap) + ".o5m")
  BUILD_OLD = ("o5m/" + (buildmap) + ".old")

  ExitCode = os.path.exists("o5m/planet.o5m")

  if ExitCode == True:
    ExitCode = os.path.exists("poly/" + (buildmap) + 
			      ".poly")
    if ExitCode == True:
      printinfo("now extracting " + (buildmap) + 
		".o5m from Planet, please wait...")
      os.system("osmconvert o5m/planet.o5m " +
                "--complete-ways --complex-ways " +
                " -B=poly/" + (buildmap) + ".poly " +
                " -o=" + (BUILD_TEMP))

      ExitCode = os.path.exists(BUILD_O5M)
      if ExitCode == True:
        os.rename((BUILD_O5M), (BUILD_OLD))

      os.rename((BUILD_TEMP), (BUILD_O5M))

      ExitCode = os.path.exists(BUILD_OLD)
      if ExitCode == True:
        os.remove(BUILD_OLD)

    else:
      printerror((work_dir) + "poly/" + (buildmap) + ".poly not found... ")
      printerror("please create or download "+ (buildmap) + ".poly")
      quit()


def update_o5m():
  os.chdir(work_dir)
  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')
  """
  set date for info in PNA

  """

  today = datetime.datetime.now()
  DATE = today.strftime('%Y%m%d_%H00')

  config.set((buildmap), 'buildday', (DATE))
  write_config()
  
  printinfo("now updating " + (buildmap) + ".o5m, please wait...")
  os.system("osmupdate --daily --hourly -B=poly/" + (buildmap) + 
	    ".poly --keep-tempfiles o5m/" + (buildmap) + 
	    ".o5m  o5m/" + (buildmap) +  "_new.o5m")

  os.chdir((work_dir) + "o5m")

  ExitCode = os.path.exists((buildmap) +  "_new.o5m")
  if ExitCode == True:
    os.rename((buildmap) + ".o5m", (buildmap) + "_temp.o5m")
    os.rename((buildmap) + "_new.o5m", (buildmap) + ".o5m")
    ExitCode = os.path.exists((buildmap) + ".o5m")
    if ExitCode == True:
      os.remove((buildmap) + "_temp.o5m")

