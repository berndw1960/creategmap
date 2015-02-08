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

          This Program create mapsets for different regions for Garmin PNA
          pygmap3.py creates only 'one' mapset, with mapset.py, it is possible
          to create mapsets from a list
        '''))
parser.add_argument('-a', '--add_mapset', dest='add_mapset', default='no')
parser.add_argument('-r', '--rm_mapset', dest='rm_mapset', default='no')
parser.add_argument('-lm', '--list_mapset', action="store_true", help="print out the mapset list")
parser.add_argument('-nz', '--no_zip', action="store_true", help="don't zip the images after build")
parser.add_argument('-d', '--del_mapset', action="store_true", help="deletes the whole list")
parser.add_argument('-c', '--contourlines', action="store_true", help="enable countourlines layer creation")
parser.add_argument('--stop_after', dest='stop_after', default='no', help='buildprocess stop after [tests|create|splitter|mkgmap]')
parser.add_argument('-l', '--log', action="store_true", help="enable splitter and mkgmap logging")
parser.add_argument('--svn', action="store_true", help="use svn versions of splitter and mkgmap")
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
if (args.add_mapset) != "no":
  if config.has_option('mapset', (args.add_mapset)) == False:
    ExitCode = os.path.exists("poly/" + (args.add_mapset) + ".poly")
    if ExitCode == False:
      print()
      printerror((WORK_DIR) + "poly/" + (args.add_mapset) + ".poly not found... ")
      print("please create or download "+ (args.add_mapset) + ".poly")
      quit()
    config.set('mapset', (args.add_mapset), 'yes')
    write_config()
  print()
  printinfo((args.add_mapset) + " added to mapset list")
  quit()

if (args.rm_mapset) != "no":
  if config.has_section('mapset') == True:
    config.remove_option('mapset', (args.rm_mapset))
    write_config()
  print()
  printwarning((args.rm_mapset) + " removed from mapset list")
  quit()

if (args.list_mapset):
  if config.has_section('mapset') == True:
    print()
    printinfo("mapset list includes: ")
    for key in (config['mapset']):
      print ("  " + (key) + " = " + config['mapset'][(key)])
  else:
    print()
    printinfo("mapset didn't exist")
  print()
  quit()

if (args.del_mapset):
  if config.has_section('mapset') == True:
    config.remove_section('mapset')
    write_config()
  printwarning("mapset list deleted")
  quit()

if (args.stop_after):
  stop = " --stop_after " + (args.stop_after)
else:
  stop = " "

if (args.contourlines):
  cl = " -c "
else:
  cl = " "

if (args.svn):
  svn = " --svn "
else:
  svn = " "

if (args.no_zip):
  zip = " "
else:
  zip = "  -z "

if (args.log):
  log = " --log "
else:
  log = " "

for buildmap in config['mapset']:
  if config['mapset'][(buildmap)] == "yes":
    ExitCode = os.path.exists("stop")
    if ExitCode == True:
      os.remove ("stop")
      print()
      printwarning("stopping build_process")
      print()
      quit()
    os.system("pygmap3.py " + (stop) + (cl) +  (svn) +  (log) + (zip) + " -b " + (buildmap))
    config.set('runtime', 'get_tools', 'no')
    write_config()

config.set('runtime', 'get_tools', 'yes')
write_config()

print()
print("###### all mapsets successfully build! #######")
print()


quit()
