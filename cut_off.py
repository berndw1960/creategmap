#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
import argparse
import time



# DEFs =============================================================================

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


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
    


"""
  argparse
  
"""

parser = argparse.ArgumentParser(
        prog='PROG', 
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\
        
            
             
            Place your own *-poly in WORK_DIR/poly,
            example for dach, use dach.poly as name
                          
            Hamburg     --> -b hamburg  
            Bayern      --> -b bayern
            Germany     --> -b germany
            D_A_CH      --> -b dach (default)
              

                        
        '''))

parser.add_argument('-b', '--buildmap', dest='buildmap', default='dach')
args = parser.parse_args()
BUILDMAP = (args.buildmap)

WORK_DIR = (os.environ['HOME'] + "/map_build/")

"""
  needed programs und dirs
  
"""


os.chdir(WORK_DIR)

hint = "osmconvert missed, needed to cut data from the planet.o5m"
checkprg("osmconvert", hint)

hint = ("No Planet-File found! ")
is_there("planet.o5m", hint)


"""
  cut data from planet-file
  
""" 


def fetch():
  BUILD_TEMP = ("o5m/" + (BUILDMAP) + ".temp.o5m")
  BUILD_O5M = ("o5m/" + (BUILDMAP) + ".o5m")
  BUILD_OLD = ("o5m/" + (BUILDMAP) + ".old")
  
  ExitCode = os.path.exists("planet.o5m")
  if ExitCode == True:
    ExitCode = os.path.exists("poly/" + (BUILDMAP) + ".poly")
    if ExitCode == True:
      printinfo("I'm now extracting " + (BUILDMAP) + ".o5m from Planet")      
      os.system("osmconvert planet.o5m " +
                "--complete-ways --complex-ways " +
                " -B=poly/" + (BUILDMAP) + ".poly " +
                " -o=" + (BUILD_TEMP))
      ExitCode = os.path.exists("tiles/" + (BUILDMAP) + "_split.lck")
      while ExitCode == True:
        time.sleep(5)
        
      ExitCode = os.path.exists(BUILD_O5M)
      if ExitCode == True:
        os.rename((BUILD_O5M), (BUILD_OLD))
        
      os.rename((BUILD_TEMP), (BUILD_O5M))
      ExitCode = os.path.exists(BUILD_OLD) 
      if ExitCode == True:
        os.remove(BUILD_OLD)
      
    else:
      printerror("tiles/" + (BUILDMAP) + ".poly not found... exit")
      quit()
         
 
fetch()

quit()
 