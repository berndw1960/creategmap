#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
import configparser
import time


def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


WORK_DIR = (os.environ['HOME'] + "/map_build/")

"""
cut data from planet-file

"""
config = configparser.ConfigParser()

def fetch():
  config.read('pygmap3.cfg')

  buildmap = config.get('runtime', 'buildmap')
  BUILD_TEMP = ("o5m/" + (buildmap) + ".temp.o5m")
  BUILD_O5M = ("o5m/" + (buildmap) + ".o5m")
  BUILD_OLD = ("o5m/" + (buildmap) + ".old")

  ExitCode = os.path.exists("planet.o5m")

  if ExitCode == True:
    ExitCode = os.path.exists("poly/" + (buildmap) + ".poly")
    if ExitCode == True:
      printinfo("I'm now extracting " + (buildmap) + ".o5m from Planet, please wait...")
      os.system("osmconvert planet.o5m " +
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
      printerror("tiles/" + (buildmap) + ".poly not found... exit")
      quit()

