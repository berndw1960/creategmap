#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
import configparser



def printinfo(msg):
  print(("II: " + msg))

def printwarning(msg):
  print(("WW: " + msg))

def printerror(msg):
  print(("EE: " + msg))
  
  
config = configparser.ConfigParser()
WORK_DIR = (os.environ['HOME'] + "/map_build/")



"""
  cut data from planet-file
  
""" 


def fetch():
  buildmap = (config.get('runtime', 'buildmap'))
  BUILD_TEMP = ((WORK_DIR) + "o5m/" + (buildmap) + ".temp.o5m")
  BUILD_O5M = ((WORK_DIR) + "o5m/" + (buildmap) + ".o5m")
  BUILD_OLD = ((WORK_DIR) + "o5m/" + (buildmap) + ".old")
  ExitCode = os.path.exists((WORK_DIR) + "planet.o5m")
  if ExitCode == True:
    ExitCode = os.path.exists((WORK_DIR) + "poly/" + (buildmap) + ".poly")
    if ExitCode == True:
      printinfo("I'm now extracting " + (buildmap) + ".o5m from Planet")      
      os.system("osmconvert planet.o5m " +
                "--complete-ways --complex-ways " +
                " -B=poly/" + (buildmap) + ".poly " +
                " -o=" + (BUILD_TEMP))
      ExitCode = os.path.exists((WORK_DIR) + "tiles/" + (buildmap) + "_split.lck")
      while ExitCode == True:
        time.sleep(5)
      os.rename((BUILD_O5M), (BUILD_OLD))
      os.rename((BUILD_TEMP), (BUILD_O5M))
      os.remove(BUILD_OLD)
    else:
      printerror((WORK_DIR) + "tiles/" + (buildmap) + ".poly not found... exit")
      quit()
         
       