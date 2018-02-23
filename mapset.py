#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import argparse

WORK_DIR = os.environ['HOME'] + "/map_build/"

def printerror(msg):
  print("EE: " + msg)
  
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
else:
  build_config.update()
  
config.read('pygmap3.cfg')


"""
argparse

"""

parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\

          This Program create mapsets for different regions for Garmin PNA
        '''))

## mapsets
parser.add_argument('-am', '--add_mapset', default=0, help="add a new poly to the mapset list. 'ALL' for every poly in " + WORK_DIR + "poly ")
parser.add_argument('-lm', '--list_mapset', action="store_true", help="print out the mapset list")
parser.add_argument('-rm', '--rm_mapset', default=0, help="remove a poly from the mapset list")
parser.add_argument('-em', '--enable_mapset', action="store_true", help="enable the whole list")
parser.add_argument('-dm', '--disable_mapset', action="store_true", help="disable the whole list")
parser.add_argument('-f', '--fastbuild', action="store_true", help="build a mapset for " + config['runtime']['default'])
parser.add_argument('-s', '--set_default', default=0, help="set region to fast build a mapset as new default")
parser.add_argument('-ba', '--break_after', default=0, help="break mapset creating after this changeset, use '-lm' for the list")

## pygmap3
parser.add_argument('-ob', '--old_bounds', action="store_true", help="use the previous used bounds")
parser.add_argument('-nz', '--no_zip', action="store_true", help="don't zip the images after build")
parser.add_argument('-c', '--contourlines', action="store_true", help="enable countourlines layer creation")
parser.add_argument('-st', '--stop_after', default=0, help='build process stop after [tests|contourlines|mapdata|splitter|mkgmap]')
parser.add_argument('-l', '--log', action="store_true", help="enable splitter and mkgmap logging")
parser.add_argument('-v', '--verbose', action="store_true", help="increase verbosity")
parser.add_argument('-mt', '--mkgmap_test', action="store_true", help="use a svn version of mkgmap like housenumbers2")
parser.add_argument('-so', '--spec_opts', action="store_true", help="use some special opts to test the raw data")

args = parser.parse_args()

"""
set, edit or delete mapset list

"""

if args.add_mapset:
  if config.has_section('mapset') == False:
    config['mapset'] = {}
  
  if args.add_mapset == "ALL":
    path = WORK_DIR + "poly"
    dir = os.listdir(path)  
    for file in dir:
      file = os.path.splitext(file)[0]
      if config['mapset'][file] == "yes":
        continue
      else:
        config.set('mapset', file, 'no')
    write_config()
    print()
    printwarning(" ALL poly files added to mapset list, but not enabled! ")
    print()
    printinfo(" To build a mapset, use '--enable_mapset' for whole list  ")
    printinfo(" or '--add_mapset' for a special file ")
    print()
    quit()
    
  else:
    file = os.path.splitext(os.path.basename(args.add_mapset))[0]
  
    if config.has_option('mapset', args.add_mapset) == False:
      if os.path.exists("poly/" + args.add_mapset + ".poly") == False:
        print()
        printerror(WORK_DIR + "poly/" + file + ".poly not found... ")
        print("please create or download " + file + ".poly")
        print()
        quit()
    config.set('mapset', args.add_mapset, 'yes')
    write_config()
    print()
    printinfo(args.add_mapset + " added to or enabled on list")
    print()
    quit()

if args.rm_mapset:
  if config.has_section('mapset'):
    config.set('mapset', args.rm_mapset, 'no')
    write_config()
  print()
  printwarning(args.rm_mapset + " disabled on list")
  print()
  quit()

if args.list_mapset:
  if config.has_section('mapset'):
    print()
    printinfo("mapset list includes: ")
    print()
    for key in (config['mapset']):
      if config['mapset'][key] == "yes":
        print ("  " + key + " = " + config['mapset'][key])
  else:
    print()
    printinfo("mapset list didn't exist or is empty")
  print()
  quit()

if args.enable_mapset:
  if config.has_section('mapset'):
    for key in (config['mapset']):
      config.set('mapset', key, 'yes')
  else:
    print()
    printerror(" mapset list not found!")
    printerror(" please create one with 'mapset.py -am dach'")
    print()
    quit()
  write_config()
  print()
  printinfo(" all mapsets enabled on list")
  print()
  quit()
  
if args.disable_mapset:
  if config.has_section('mapset'):
    for key in (config['mapset']):
      config.set('mapset', key, 'no')
  write_config()
  print()
  printwarning(" all mapsets disabled on list")
  print() 
  quit()

if args.set_default:
  if os.path.exists("poly/" + args.set_default + ".poly") == False:
    print()
    printerror((WORK_DIR) + "poly/" + args.set_default + ".poly not found... ")
    printerror("please create or download "+ args.set_default + ".poly")
    print()
    quit()

  config.set('runtime', 'default', args.set_default)
  print(args.set_default + " set as new default region")
  print()
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

if args.spec_opts:
  so = " -so "
else:
  so = " "
  
command_line =  "pygmap3.py -kg " + verbose + stop + cl + mkgmap_test + log + zip + ob

if args.fastbuild:
  buildmap = config['runtime']['default']
  if args.verbose:
    print()
    print(command_line)

  os.system(command_line)

    
else:
  for buildmap in config['mapset']:
    if config['mapset'][buildmap] == "yes":
      if buildmap == args.break_after:
        print()
        printwarning("Stopping creating mapsets after this mapset")
      if os.path.exists("stop") == True:
        os.remove ("stop")
        print()
        printwarning("stopped build_process")
        print()
        quit()

      os.system(command_line + "-p " + buildmap)
      
    if buildmap == args.break_after:
      quit()

  print()
  print("###### all mapsets successfully build! #######")
  print()


quit()
