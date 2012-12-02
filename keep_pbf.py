#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""
  keep_pbf on/off
  no options - no harm
"""


import os
import sys

# DEFs =============================================================================

def printinfo(msg):
  print(("II: " + msg))

def printwarning(msg):
  print(("WW: " + msg))

def printerror(msg):
  print(("EE: " + msg))


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
    quit()
    

WORK_DIR = (os.environ['HOME'] + "/map_build/")

hint = ("mkdir " + (WORK_DIR))
is_there((WORK_DIR), hint) 

os.chdir(WORK_DIR)

ExitCode = os.path.exists("keep_pbf.lck")
if ExitCode == True:
  os.remove("keep_pbf.lck")
  printinfo("keep_pbf switched off!")
else:
  datei = open("keep_pbf.lck", "w")
  datei.close()
  printinfo("keep_pbf switched on!")
  
quit()  
