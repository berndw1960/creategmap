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

work_dir = (os.environ['HOME'] + "/share/osm/map_build/")

hint = ("mkdir " + (work_dir))
checkdir((work_dir), hint) 

os.chdir(work_dir)

ExitCode = os.system("test -f keep_pbf.lck")
if ExitCode == 0:
  os.system("rm -f keep_pbf.lck")
  printinfo("keep_pbf switched off!")
else:
  os.system("touch keep_pbf.lck")
  printinfo("keep_pbf switched on!")
  
quit()  
