#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import configparser
import os
import argparse

WORK_DIR = os.environ['HOME'] + "/map_build/"


"""
set prefix for messages

"""

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


"""
argparse

"""

parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\
          
          to create mapsets of often build maps, you can edit the mapset list with
            
                                    
            'mapset.py -b dach -m add'          add 'dach' to the mapset list
            'mapset.py -b dach -m remove'       remove 'dach' from the mapset list
            'mapset.py -m list'                 print out the mapset list
            'mapset.py -m delete'               deletes the whole list
            
        '''))
parser.add_argument('-m', '--mapset', dest='mapset', default='no')
parser.add_argument('-b', '--buildmap', dest='buildmap', default='dach')
args = parser.parse_args()


"""
test if a file or dir can be found at a predefined place
raise message if fails and returns 1
on success return 0
"""

ExitCode = os.path.exists(WORK_DIR)
if ExitCode == False:
  printerror("Please create" + (WORK_DIR))
  quit()

os.chdir(WORK_DIR)


"""
configparser

"""

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

config = configparser.ConfigParser()


import build_config

ExitCode = os.path.exists("pygmap3.cfg")
if ExitCode == False:
  build_config.create()

config.read('pygmap3.cfg')

if config.has_section('mapset') == False:
    config['mapset'] = {}
    write_config()
    
config.read('pygmap3.cfg')   

"""
set, edit or delete mapset list

"""
if (args.mapset) == "add":
  if config.has_option('mapset', (args.buildmap)) == False:
    config.set('mapset', (args.buildmap), 'yes')
    write_config()

  printinfo((args.buildmap) + " added to mapset list")
  quit()

elif (args.mapset) == "remove":
  if config.has_section('mapset') == True:
    config.remove_option('mapset', (args.buildmap))
    write_config()
  printwarning((args.buildmap) + " removed from mapset list")
  quit()

elif (args.mapset) == "list":
  if config.has_section('mapset') == True:
    printinfo("mapset list includes: ")
    for key in (config['mapset']):
      print ("  " + (key) + " = " + config['mapset'][(key)])
  else:
    printwarning("mapset list not found")
  quit()
  
elif (args.mapset) == "delete":
  if config.has_section('mapset') == True:
    config.remove_section('mapset')
    write_config()
  printwarning("mapset list deleted")
  quit()                         
 
for buildmap in config['mapset']:
  if config['mapset'][(buildmap)] == "yes":
    os.system("pygmap3 -b " + (buildmap))

printinfo("")
printinfo("")
printinfo("###### all mapsets successful build! #######")
printinfo("")
printinfo("")
   
quit()    
