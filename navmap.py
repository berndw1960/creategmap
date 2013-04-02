#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import http.client
import re
import configparser


def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


WORK_DIR = os.environ['HOME'] + "/map_build/"

config = configparser.ConfigParser()

def bounds():

  config.read('pygmap3.cfg')

  """
  boundaries from navmap.eu
  """

  if config.get('navmap', 'bounds') == "yes":
   
    ExitCode = os.path.exists("sea.zip")
    if ExitCode == False:
      printerror("precompiled sea_bound in sea.zip not found")
      printerror("please download the precompiled sea_bounds from")
      printerror("http://www.navmaps.org/boundaries")
      printerror("and store as sea.zip")
      quit()

    ExitCode = os.path.exists("bounds.zip")
    if ExitCode == False:
      printerror("precompiled bounds in bounds.zip not found")
      printerror("please download the precompiled bounds from")
      printerror("http://www.navmaps.org/boundaries")
      printerror("and store as bounds.zip")
      quit() 
    
    