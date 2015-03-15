#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import configparser
import os
import argparse

WORK_DIR = os.environ['HOME'] + "/map_build/"

"""
test if a file or dir can be found at a predefined place
raise message if fails and returns 1
on success return 0
"""

if os.path.exists(WORK_DIR) == False:
  printerror("Please create" + WORK_DIR)
  quit()

os.chdir(WORK_DIR)


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
configparser

"""

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

config = configparser.ConfigParser()
import build_config

if os.path.exists("pygmap3.cfg") == False:
  build_config.create()

config.read('pygmap3.cfg')


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

## mapsets
parser.add_argument('-a', '--add_mapset', dest='add_mapset', default='no')
parser.add_argument('-lm', '--list_mapset', action="store_true", help="print out the mapset list")
parser.add_argument('-r', '--rm_mapset', dest='rm_mapset', default='no')
parser.add_argument('-d', '--del_mapset', action="store_true", help="deletes the whole list")
parser.add_argument('-f', '--fastbuild', action="store_true", help="build a mapset for " + config['runtime']['default'])
parser.add_argument('-s', '--set_default', dest='set_default', default='no', help="set region to fast build a mapset as new default")

## pygmap3
parser.add_argument('-ob', '--old_bounds', action="store_true", help="use the previous used bounds")
parser.add_argument('-nz', '--no_zip', action="store_true", help="don't zip the images after build")
parser.add_argument('-c', '--contourlines', action="store_true", help="enable countourlines layer creation")
parser.add_argument('-st', '--stop_after', dest='stop_after', default='no', help='buildprocess stop after [tests|contourlines|mapdata|splitter|mkgmap]')
parser.add_argument('-l', '--log', action="store_true", help="enable splitter and mkgmap logging")
parser.add_argument('-v', '--verbose', action="store_true", help="increase verbosity")
parser.add_argument('-mt', '--mkgmap_test', action="store_true", help="use a svn version of mkgmap like housenumbers2")

args = parser.parse_args()

"""
set, edit or delete mapset list

"""

if args.add_mapset != "no":
  if config.has_section('mapset') == False:
    config['mapset'] = {}

  if config.has_option('mapset', args.add_mapset) == False:
    if os.path.exists("poly/" + args.add_mapset + ".poly") == False:
      print()
      printerror(WORK_DIR + "poly/" + args.add_mapset + ".poly not found... ")
      print("please create or download "+ args.add_mapset + ".poly")
      quit()
    config.set('mapset', args.add_mapset, 'yes')
    write_config()
  print()
  printinfo(args.add_mapset + " added to mapset list")
  quit()

if args.rm_mapset != "no":
  if config.has_section('mapset') == True:
    config.remove_option('mapset', args.rm_mapset)
    write_config()
  print()
  printwarning(args.rm_mapset + " removed from mapset list")
  quit()

if args.list_mapset:
  if config.has_section('mapset') == True:
    print()
    printinfo("mapset list includes: ")
    for key in (config['mapset']):
      print ("  " + key + " = " + config['mapset'][key])
  else:
    print()
    printinfo("mapset didn't exist")
  print()
  quit()

if args.del_mapset:
  if config.has_section('mapset') == True:
    config.remove_section('mapset')
    write_config()
  printwarning("mapset list deleted")
  quit()


if args.set_default != "no":
  if os.path.exists("poly/" + args.set_default + ".poly") == False:
    print()
    printerror((WORK_DIR) + "poly/" + args.set_default + ".poly not found... ")
    printerror("please create or download "+ args.set_default + ".poly")
    print()
    quit()

  config.set('runtime', 'default', args.set_default)
  print(args.set_default + " set as new default region")

  write_config()
  quit()


## build or additional option for pygmap3


if args.stop_after:
  stop = "-st " + args.stop_after + " "
else:
  stop = ""

if args.contourlines:
  cl = "-c "
else:
  cl = ""

if args.mkgmap_test and config.has_option('runtime', 'mkgmap_test'):
  mkgmap_test = "-mt "
else:
  mkgmap_test = ""

if args.no_zip:
  zip = ""
else:
  zip = "-z "

if args.verbose:
  verbose = "-v "
else:
  verbose = ""

if args.log:
  log = "--log "
else:
  log = ""

if args.old_bounds:
  ob = "-ob "
else:
  ob = ""

command_line =  "pygmap3.py " + verbose + stop + cl + mkgmap_test + log + zip + ob

if args.fastbuild:
  buildmap = config['runtime']['default']
  if args.verbose:
    print()
    print(command_line + "-b " + buildmap)

  os.system(command_line + "-b " + buildmap)

else:
  for buildmap in config['mapset']:
    if config['mapset'][buildmap] == "yes":
      if os.path.exists("stop") == True:
        os.remove ("stop")
        print()
        printwarning("stopped build_process")
        print()
        quit()

      os.system(command_line + "-b " + buildmap)

  print()
  print("###### all mapsets successfully build! #######")
  print()


quit()
