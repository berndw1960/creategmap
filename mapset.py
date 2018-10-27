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

if config.has_section('mapset_backup'):
  if config.has_section('mapset'):
    config.remove_section('mapset')
  config.add_section('mapset')
  for key in (config['mapset_backup']):
    config.set('mapset', key, config['mapset_backup'][key])
    config.remove_option('mapset_backup', key)
  config.remove_section('mapset_backup')
  
write_config()    

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
parser.add_argument('-am', '--add_mapset', default=0, nargs='*', help="add  a space separated list of mapsets")
parser.add_argument('-ap', '--add_poly', action="store_true", help="add mapsets using all poly files in " + WORK_DIR + "poly")
parser.add_argument('-af', '--add_folder', action="store_true", help="add mapsets using the names of the folders in " + WORK_DIR + "gps_ready/zipped")
parser.add_argument('-ao', '--add_o5m', action="store_true", help="add mapsets using the names of the o5m files in " + WORK_DIR + "o5m")
parser.add_argument('-em', '--enable_mapset', default=0, nargs='*', help="enable a space separated list of mapsets, ALL for all mapsets on the list")
parser.add_argument('-dm', '--disable_mapset', default=0, nargs='*', help="disable a space separated list of mapsets, ALL for all mapsets on the list")
parser.add_argument('-rm', '--remove_mapset', default=0, nargs='*', help="delete a space separated list of mapsets, ALL for all mapsets on the list")
parser.add_argument('-lm', '--list_mapset', action="store_true", help="print out the mapset list")
parser.add_argument('-f', '--fastbuild', default=0, nargs='*', help="a space separated list of mapsets")
parser.add_argument('-ba', '--break_after', default=0, help="break mapset creating after this changeset, use '-lm' for the list")

## pygmap3
parser.add_argument('-nz', '--no_zip', action="store_true", help="don't zip the images after build")
parser.add_argument('-c', '--contourlines', action="store_true", help="enable countourlines layer creation")
parser.add_argument('-st', '--stop_after', default=0, help='build process stop after [tests|contourlines|mapdata|splitter|mkgmap]')
parser.add_argument('-l', '--log', action="store_true", help="enable splitter and mkgmap logging")
parser.add_argument('-v', '--verbose', action="store_true", help="increase verbosity")
parser.add_argument('-mt', '--mkgmap_test', action="store_true", help="use a svn version of mkgmap like housenumbers2")
parser.add_argument('-so', '--spec_opts', action="store_true", help="use some special opts to test the raw data")

args = parser.parse_args()

def mapset_backup():
  if config.has_section('mapset_backup') == False:
    config.add_section('mapset_backup')
  for key in (config['mapset']):
    config.set('mapset_backup', key, config['mapset'][key])
  print()
  printinfo("Previous mapset list is backuped!")
   
def mapset_list():
  printinfo("These folders in " + path + " are added to mapset list! ")
  print()
  for key in (config['mapset']):
    if config['mapset'][key] == "yes":
      print("  " + key)   


"""
set, edit or delete mapset list

"""

if args.add_poly:
  path = WORK_DIR + "poly"
  dir = sorted(os.listdir(path))
  for file in dir:
    file = os.path.splitext(file)[0]
    if config.has_option('mapset', file) == True:
      continue
    else:
      config.set('mapset', file, 'no')
  write_config()
  print()
  printwarning("ALL poly files added to mapset list, but not enabled! ")
  print()
  printinfo("To enable a mapset, use '--enable_mapset ALL' for whole list  ")
  printinfo("or '--enable_mapset $POLY' for a special mapset ")
  print()
  quit()
  
if args.add_folder:
  mapset_backup()
  path = WORK_DIR + "gps_ready/zipped"
  dir = sorted(os.listdir(path))
  for folder in dir:
    if config.has_option('mapset', folder) == True:
      continue
    else:
      config.set('mapset', folder, 'yes')
  for key in (config['mapset']):
    config.set('mapset', key, 'yes')
  write_config()
  mapset_list()
  print()

if args.add_mapset:
  print()
  for i in args.add_mapset:
    file = os.path.splitext(os.path.basename(i))[0]
    if config.has_option('mapset', i) == False:
      if os.path.exists("poly/" + i + ".poly") == False:
        print()
        printerror(WORK_DIR + "poly/" + file + ".poly not found... ")
        print("please create or download " + file + ".poly")
        print()
        quit()
    config.set('mapset', i, 'yes')
    print("  " + i + " added to the list ")
  write_config()
  print()

if args.add_o5m:
  mapset_backup()
  print()
  for i in os.listdir("o5m"):
    file = os.path.splitext(os.path.basename(i))[0]
    if config.has_option('mapset', file) == False:
      config.set('mapset', file, 'yes')
    print("  " + file + " added to the list ")
  write_config()
  print()

if args.enable_mapset == "ALL":
  mapset_backup()
  for key in (config['mapset']):
    config.set('mapset', key, 'yes')
  write_config()
  mapset_list()
  print()
elif args.enable_mapset:
  print()
  for i in args.enable_mapset:
    config.set('mapset', i, 'yes')
    printinfo("  " + i + " enabled!")
  write_config()
  print()

if args.disable_mapset == "ALL":
  for key in (config['mapset']):
    config.set('mapset', key, 'no')
  write_config()
  print()
  printinfo("all mapsets disabled on list")
  print()
elif args.disable_mapset:
  print()
  for i in args.disable_mapset:
    config.set('mapset', i, 'no')
    printwarning("  " + i + " disabled on list")
  write_config()
  print()

if args.remove_mapset == "ALL":
  config.remove_section('mapset')
  write_config()
  print()
  printwarning("all mapsets deleted, list is empty")
  print() 
elif args.remove_mapset:
  print()
  for i in args.remove_mapset:
    config.remove_option('mapset', i)
    printwarning("   " + i + " deleted from the list")
  write_config()
  print() 

if args.list_mapset:
  if config.has_section('mapset'):
    print()
    printinfo("mapset list includes: ")
    print()
    print("enabled:")
    for key in (config['mapset']):
      if config['mapset'][key] == "yes":
        print("  " + key)
    print()
    print("disabled:")
    for key in (config['mapset']):
      if config['mapset'][key] == "no":
        print("  " + key)  
  else:
    print()
    printinfo("mapset list didn't exist")
  print()

if args.add_mapset or args.enable_mapset or args.disable_mapset or args.disable_mapset or args.remove_mapset or args.list_mapset:
  quit()
  
if args.fastbuild:
  mapset_backup()
  for key in (config['mapset']):
    config.set('mapset', key, 'no')
  print()
  for i in args.fastbuild:
    config.set('mapset', i, 'yes')
    printinfo("  " + i + " enabled!")
  write_config()
  print()

  
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

if args.spec_opts:
  so = " -so "
else:
  so = " "
  
command_line =  "pygmap3.py -kg " + verbose + stop + cl + mkgmap_test + log + zip

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
