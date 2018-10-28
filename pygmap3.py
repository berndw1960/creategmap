#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
version 3 as published by the Free Software Foundation.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.
You should have received a copy of this license along
with this program; if not, see http://www.gnu.org/licenses/.


"""
__version__ = "0.9.50"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2014 Bernd Weigelt"
__credits__ = "Franco B."
__license__ = "AGPLv3"
__maintainer__ = "Bernd Weigelt"
__email__ = "weigelt.bernd@web.de"
__status__ = "RC"

"""
pygmap3.py, a script to build maps for GARMIN PNAs

Work in progress, be sure, that you ran it in
the knowledge, that it can be harmful for your data,
but i hope, it's safe.


Following Software is needed.

Please install them manually, they have to be
compiled on your system:

osmconvert
http://wiki.openstreetmap.org/wiki/Osmconvert
osmupdate
http://wiki.openstreetmap.org/wiki/Osmupdate

phyghtmap (to create the contourlines)
http://katze.tfiu.de/projects/phyghtmap/


Tools will be installed by the script:

mkgmap and splitter from
http://www.mkgmap.org.uk
and some other things

This files should downloaded manually
precomp_sea from navmap.org
boundaries from navmap.org

"""

#import sys
import os
import datetime
import time
import argparse
import configparser
import shutil

## local modules
import build_config
import get_tools
import navmap
import geonames
import contourlines
import mapdata
import splitter
import mkgmap
import store

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
test if a file or dir can be found at a predefined place
raise message if fails and returns 1
on success return 0
"""

if os.path.exists(WORK_DIR) == False:
  print()
  printerror("Please create " + WORK_DIR)
  print()
  quit()

os.chdir(WORK_DIR)

if os.path.exists("pygmap3.cfg"):
  if os.path.exists("pygmap3.cfg.bak"):
    os.remove("pygmap3.cfg.bak")

  shutil.copyfile('pygmap3.cfg', 'pygmap3.cfg.bak')


"""
create dir o5m, areas, poly and tiles

"""

for dir in ['o5m', 'areas', 'poly', 'tiles', 'precomp']:
  if os.path.exists(dir) == False:
    os.mkdir(dir)

"""
configparser

"""

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

config = configparser.ConfigParser()

"""
create a new config if needed

"""

if os.path.exists("pygmap3.cfg") == False:
  build_config.create()

build_config.update()

config.read('pygmap3.cfg')

if config.has_section('map_styles_backup'):
  if config.has_section('map_styles'):
    config.remove_section('map_styles')
  config.add_section('map_styles')  
  for key in (config['map_styles_backup']):
    config.set('map_styles', key, config['map_styles_backup'][key])
    config.remove_option('map_styles_backup', key)
  config.remove_section('map_styles_backup')
 
write_config()

"""
argparse

"""

parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\

            To build maps for Garmin PNA

            map layers (routable):
            basemap - to route motorvehicle, bicycle and pedestrian
            bikemap - better visibility of cycleroutes and -ways
            carmap  - only for motorvehicle, no special routing for bicycle and pedestrian

            additional layers
            fixme   - a fixme layer for mapping
            boundary - a layer to show boundaries with admin_level<=6

            Place your own *-poly in WORK_DIR/poly,
            example for dach, use dach.poly as name

        '''))
        
        
parser = argparse.ArgumentParser(
         prog='PROG',
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# Java options
parser.add_argument('-xmx', '--xmx', default=config['java']['xmx'], help="""set the HEAP for Java, min. 500 MB per threads, 
                                                                               an example '6G' or '6000M' for a CPU with 4 cores 
                                                                               and 8 threads. """)
parser.add_argument('-xms', '--xms', default=config['java']['xms'], help="""set the HEAP, could be the same value as -Xmx,
                                                                               but a different value is possible """)
parser.add_argument('-agh', '--aggressiveheap', action="store_true", help="""set the HEAP permanent in an aggressive mode""")
parser.add_argument('-no_agh', '--no_aggressiveheap', action="store_true", help="""disable the aggressive mode """)

# mapset handling
parser.add_argument('-p', '--poly', dest='poly', default=config['runtime']['default'], help="set map region to build")
parser.add_argument('-lp', '--list_poly', action="store_true", help="list all poly files in " + WORK_DIR + "poly ")
parser.add_argument('-s', '--set_default', dest='set_default', default=0, help="set region to build as new default")
parser.add_argument('-ntl', '--name-tag-list', dest='name_tag_list', default=0, help="which name tag should be used for naming objects")

# mapstyle handling
parser.add_argument('-lm', '--list_mapstyle', action="store_true", help="list the style settings")
parser.add_argument('-a', '--add_style', default=0, help="add a new style")
parser.add_argument('-m', '--map_style', default=0, help="enable/disable a style")
parser.add_argument('-r', '--rm_style', default=0, help="remove a style")
parser.add_argument('-am', '--all_map_styles', action="store_true", help="enable all map_styles")
parser.add_argument('-dm', '--no_map_styles', action="store_true", help="disable all map_styles")
parser.add_argument('-u', '--use_style', default=0, nargs='*', help="use only one style")

# mapdata
parser.add_argument('-k', '--keep_data', action="store_true", help="don't update the mapdata")
parser.add_argument('-nb', '--new_bounds', action="store_true", help="try to get precomp sea or bounds")
parser.add_argument('-ub', '--use_bounds', default=0, help="use a special bounds file")
parser.add_argument('-us', '--use_sea', default=0, help="use a special sea file")
parser.add_argument('-lb', '--list_bounds', action="store_true", help="list the local precomp sea or bounds")
parser.add_argument('--hourly', action="store_true", help="update the raw mapdata with the hourly files")
parser.add_argument('--minutely', action="store_true", help="update the raw mapdata with the minutely files")

# splitter options
parser.add_argument('-na', '--no_areas_list', action="store_true", help=" don't use areas.list to split mapdata")
parser.add_argument('-ns', '--no_split', action="store_true", help="don't split the mapdata")
parser.add_argument('-mn', '--maxnodes', help="set the maxnodes for splitter")

# mkgmap options
parser.add_argument('-mj', '--max_jobs', default='yes', help=" set the used threads to use with mkgmap (yes(max)/no(=1)/$NUM_THREADS)")
parser.add_argument('-kg', '--keep_going', action="store_true", help=False)
parser.add_argument('-i', '--installer', action="store_true", help="create mapsource installer")

# contourlines and hillshading
parser.add_argument('-tdb', '--tdb', action="store_true", help="create hillshading only for the next build process")
parser.add_argument('-sw_tdb', '--switch_tdb', action="store_true", help="enable/disable creating hillshading permanent")
parser.add_argument('-et', '--enable_tdb', default=0, help="enable the hillshading for one mapstyle, use 'ALL' for every entry in the list")
parser.add_argument('-dt', '--disable_tdb', default=0, help="disable the hillshading for one mapstyle, use 'ALL' for every entry in the list")
parser.add_argument('-lv', '--levels', default=config['maplevel']['levels'], help="""This is a number between 0 and 16
                                                                                     (although perhaps numbers above 10 are not usable), 
                                                                                      with 0 corresponding to the most detailed view.""") 
parser.add_argument('-dd', '--dem_dists', default=config['demtdb']['demdists'], help="""set the distance between two points with height information, 
                                                                                         a multiple of '3314'""")
parser.add_argument('-c', '--contourlines', action="store_true", help=False)
parser.add_argument('-edu', '--ed_user', default=0, help=False)
parser.add_argument('-edp', '--ed_pwd', default=0, help=False)                    

# image handling
parser.add_argument('-z', '--zip_img', action="store_true", help=False)

# debugging
parser.add_argument('-cs', '--check_styles', action="store_true", help=False)
parser.add_argument('-st', '--stop_after', default=0, help='[get_tools|contourlines|mapdata|splitter|mkgmap]')
parser.add_argument('-so', '--spec_opts', action="store_true", help="use some special opts to test the raw data")
parser.add_argument('-v', '--verbose', action="store_true", help=False)
parser.add_argument('-l', '--log', action="store_true", help=False)

# development
parser.add_argument('-mt', '--mkgmap_test', action="store_true", help="use a svn version of mkgmap")
parser.add_argument('-ms', '--mkgmap_set', default=0, help="set a svn version of mkgmap like dem-tdb")

args = parser.parse_args()

if args.list_poly:
  path = WORK_DIR + "poly"
  dir = sorted(os.listdir(path))  
  print()
  printinfo(" This poly files are in '" + WORK_DIR +"poly': ")
  print()
  for file in dir:
    file = os.path.splitext(file)[0]
    print(file)
  print()  
  quit()

 
"""
set buildmap

"""

buildmap = os.path.splitext(os.path.basename(args.poly))[0]
config.set('runtime', 'buildmap', buildmap)

write_config()

name_tag_list = args.name_tag_list
if config.has_section('name_tag_list') == False:
  config.add_section('name_tag_list')
  config.set('name_tag_list', 'default', 'name:en,name:int,name')
  write_config()
  
if args.name_tag_list:
  config.set('name_tag_list', buildmap, name_tag_list) 

if config.has_option('name_tag_list', buildmap) == False:
  print()
  printwarning("for this mapset the MKGMAP option '--name-tag-list' isn't set")
  printwarning("using the default 'name:en,name:int,name'")
  print()

# map build options

if args.list_mapstyle:
  if config.has_section('map_styles'):
    print()
    printinfo("map_styles list includes: ")
    print()
    print(" enabled:")
    for key in (config['map_styles']):
      if config['map_styles'][key] == "yes":
        print("  " + key)
    print()
    print(" disabled:")
    for key in (config['map_styles']):
      if config['map_styles'][key] == "no":
        print("  " + key)
    if config.has_section('mapset') == True:
      print()
      printinfo("mapset list includes: ")
      
      if config.has_option('runtime', 'default'):
        print()
        print(" default:")
        print("  " + config['runtime']['default']) 
      print()
      print(" enabled:")
      for key in (config['mapset']):
        if config['mapset'][key] == "yes":
          print("  " + key)
      print()
      print(" disabled:")
      for key in (config['mapset']):
        if config['mapset'][key] == "no":
          print("  " + key)
  print()
  quit()

if args.all_map_styles:
  if config.has_section('map_styles'):
    print()
    for key in (config['map_styles']):
      config.set('map_styles', key, 'yes')
      write_config()      
      print("  " + key + " = " + config['map_styles'][key])

    print()
    printinfo("all mapstyles enabled")
    print()
  quit()

if args.no_map_styles:
  if config.has_section('map_styles'):
    print()
    for key in (config['map_styles']):
      config.set('map_styles', key, 'no')
      print("  " + key + " = " + config['map_styles'][key])

    write_config()
    print()
    printinfo("all mapstyles disabled,")
    printinfo("please enable at least one mapstyle before the next build")
    printinfo("as example 'pygmap3.py -m basemap'")
    print()
  quit()

def info_styles():
  print()
  printerror(args.add_style + "_style - dir not found")
  print()
  print()
  printinfo("possible styles for routable layers are: ")
  print("    basemap")
  print("    bikemap")
  print("    carmap")
  print()
  print("    defaultmap")
  print()
  printinfo("possible styles as overlays are:")
  print("    bikeroute")
  print("    boundary")
  print("    fixme")
  print()
  print()
  print("    or your own style files!")
  print()

if args.add_style:
  if os.path.exists("styles/" + args.add_style + "_style"):
    config.set('map_styles', args.add_style, 'yes')
    print()
    if args.add_style in config == False:
      printinfo("please add a section [" + args.add_style + "] to pygmap3.cfg")
      print("see the existing entries for the fixme layer as example")
      print("for family-id and product-id increase the values")
      print("mapid_ext and draw_priotity could be the same values")
      print("family_name is a free text value")
      print()
      printinfo("please read mkgmap's manual for more infos")
      print()
      print("  [fixme]")
      for key in config['fixme']:
        print("  " + key + " = " + config['fixme'][key])
      print()
    printinfo(args.add_style + " added to map_styles list")
  elif args.add_style == "defaultmap":
    config.set('map_styles', args.add_style, 'yes')
  else:
    info_styles()
  print()
  write_config()
  quit()

if args.map_style and args.map_style != "defaultmap":
  if os.path.exists("styles/" + args.map_style + "_style") == False:
    info_styles()
    quit()

if args.map_style:
  if config.has_option('map_styles', args.map_style):
    if config['map_styles'][args.map_style] == "yes":
      config.set('map_styles', args.map_style, 'no')
      print()
      printwarning(args.map_style + " style disabled")
    elif config['map_styles'][args.map_style] == "no":
      config.set('map_styles', args.map_style, 'yes')
      print()
      printinfo(args.map_style + " style enabled")
  else:
     config.set('map_styles', args.map_style, 'yes')
     print()
     printinfo(args.map_style + " style added and enabled")

  write_config()
  quit()

if args.rm_style:
  if config.has_option('map_styles', args.rm_style):
    config.remove_option('map_styles', args.rm_style)
    write_config()
  print()
  printinfo(args.rm_style + " removed from map_styles list")
  print()
  quit()

if args.use_style:
  if config.has_section('map_styles_backup') == False:
    config.add_section('map_styles_backup')
  for key in (config['map_styles']):
    config.set('map_styles_backup', key, config['map_styles'][key])
    config.set('map_styles', key, 'no')
  print()
  printinfo("create a map with these styles: ")
  print()
  for i in args.use_style:
    config.set('map_styles', i, 'yes')
    print("   " + i)
    
  print()
  
if args.set_default:
  if os.path.exists("poly/" + args.set_default + ".poly") == False:
    print()
    printerror((WORK_DIR) + "poly/" + args.set_default + ".poly not found... ")
    printerror("please create or download " + args.set_default + ".poly")
    print()
    quit()

  config.set('runtime', 'default', args.set_default)
  print(args.set_default + " set as new default region")

  write_config()
  quit()
 
if args.check_styles:

  mkgmap.check()
  quit()
  
"""
special opts to debug the raw map data
"""

if args.spec_opts:
  config.set('runtime', 'use_spec_opts', '1')

"""
logging

"""

if args.log:
  config.set('runtime', 'logging', '1')

"""
verbosity

"""

if args.verbose:
  config.set('runtime', 'verbose', '1')

"""
HEAP size for java, default is aggressiveheap
"""

if args.aggressiveheap:
  config.set('java', 'agh', '1')

if args.no_aggressiveheap:
  config.set('java', 'agh', '0') 

if config['java']['agh'] == "0":
    if args.xmx != config['java']['xmx']:
      config.set('java', 'xmx', "-Xmx" + str(args.xmx))
    if args.xms != config['java']['xms']:
      config.set('java', 'xms', "-Xms" + str(args.xms))

  
"""
maxnodes for splitter

"""

if config.has_option('maxnodes', buildmap) == False:
  config.set('maxnodes', buildmap, config['maxnodes']['default'])
  
if args.maxnodes:
  if args.maxnodes != config['maxnodes'][buildmap]:
    config.set('maxnodes', buildmap, args.maxnodes)
    if os.path.exists("areas/" + buildmap + "_areas.list"):
      os.remove("areas/" + buildmap + "_areas.list")

"""
don't use the areas.list

"""

if args.no_areas_list:
  if os.path.exists("areas/" + buildmap + "_areas.list"):
    os.remove("areas/" + buildmap + "_areas.list")


"""
development version of splitter and mkgmap

"""

if args.mkgmap_set:
  config.set('runtime', 'mkgmap_test', args.mkgmap_set)
  write_config()
  print()
  printinfo(" MKGMAP test version set to " + args.mkgmap_set)
  print()
  printinfo(" use this version with pygmap3 -mt ")
  print()
  quit()

if args.mkgmap_test:
  if config.has_option('runtime', 'mkgmap_test') == True:
    config.set('runtime', 'use_mkgmap_test', '1')
  else:
    print()
    printwarning("no test version of mkgmap is set in config")
    printwarning("please use '-ms/--mkgmap_set' to set one version")
    print()
    quit()

""""
set the amount of levels
"""

if args.levels != config['maplevel']['levels']:
  config.set('maplevel', 'levels', args.levels)

"""
max-jobs for mkgmap

"""

if args.max_jobs:
  config.set('runtime', 'max_jobs', args.max_jobs)

"""
keep_going on errors

"""

if args.keep_going:
  config.set('runtime', 'keep_going', "1")
  
"""
create the contourlines and hillshading

"""

if args.switch_tdb and config['demtdb']['switch_tdb'] == "no":
  config.set('demtdb', 'switch_tdb', "yes")
  config.set('runtime', 'tdb', "yes")
  print()
  printinfo("hillshading enabled")
  print()
elif args.switch_tdb and config['demtdb']['switch_tdb'] == "yes":
  config.set('demtdb', 'switch_tdb', "no")
  config.set('runtime', 'tdb', "no")
  print()
  printinfo("hillshading disabled")
  print()
elif config['demtdb']['switch_tdb'] == "yes":
  config.set('runtime', 'tdb', "yes")
elif args.tdb:
  config.set('runtime', 'tdb', "yes")
else:
  config.set('demtdb', 'switch_tdb', "no")
  config.set('runtime', 'tdb', "no")

if args.enable_tdb:
  if args.enable_tdb == "ALL":  
    print()
    for key in (config['tdblayer']):
      config.set('tdblayer', key, "yes")
      print ("  " + key + " = " + config['tdblayer'][key])
    print()
  else:
    config.set('tdblayer', args.enable_tdb, "yes")
    print()
    print( "  enabled hillshading for " + args.enable_tdb + " layer! " )
    print()
  write_config()
  quit()
  
if args.disable_tdb:
  if args.disable_tdb == "ALL":  
    print()
    for key in (config['tdblayer']):
      config.set('tdblayer', key, "no")
      print ("  " + key + " = " + config['tdblayer'][key])
    print()
  else:
    config.set('tdblayer', args.disable_tdb, "no")
    print()
    print( "  disabled hillshading for " + args.disable_tdb + " layer! " )
    print()
  write_config()
  quit()

if args.dem_dists != config['demtdb']['demdists']:
  config.set('demtdb', 'demdists', args.dem_dists)
  
if args.ed_user:
  config.set('runtime', 'ed_user', args.ed_user)

if args.ed_pwd:      
  config.set('runtime', 'ed_pwd', args.ed_pwd)
  
"""
set or create the mapid

"""

if config.has_option('mapid', buildmap) == True:
  option_mapid = config['mapid'][buildmap]
else:
  option_mapid = config['mapid']['next_mapid']
  next_mapid = str(int(option_mapid)+1)
  config.set('mapid', buildmap, option_mapid)
  config.set('mapid', 'next_mapid', next_mapid)

write_config()

if args.verbose:
  print()
  print(" switch_tdb = " + config['demtdb']['switch_tdb'])
  print("    tdb = " + config['runtime']['tdb'])
  print()

"""
osmupdate and osmconvert

"""

if config['osmtools']['check'] == "yes":
  def checkprg(programmtofind, solutionhint):
    if os.system("which " + programmtofind) == 0:
      print()
      printinfo(programmtofind + " found")
    else:
      print()
      printerror(programmtofind + " not found")
      print(solutionhint)
      quit()

  for tool in ['osmconvert', 'osmupdate']:
    hint = tool + " missed, please use mk_osmtools to build it from sources"
    print()
    checkprg(tool, hint)

  config.set('osmtools', 'check', 'no')
  write_config()

"""
get splitter and mkgmap

"""

get_tools.from_mkgmap_org()

config.read('pygmap3.cfg')

"""
get the geonames file

"""

geonames.cities15000()

"""
bounds and precomp_sea

"""
if args.list_bounds:
  navmap.list_bounds()
  quit()

if args.new_bounds:
  navmap.latest_bounds()
  config.set('bounds', 'bounds', "bounds-latest.zip")
  config.set('bounds', 'sea', "sea-latest.zip")

if args.use_bounds:
  config.set('bounds', 'bounds', args.use_bounds)
if args.use_sea:
  config.set('bounds', 'sea', args.use_sea)

write_config() 

if args.list_bounds or args.use_bounds:
  navmap.fetch_bounds()

"""
--stop_after get_tools

"""
config.read('pygmap3.cfg')
if args.stop_after == "get_tools":
  print()
  printinfo("needed programs found and files successfully loaded")
  print()
  quit()

"""
create an installer for mapsource

"""
if args.installer:
  config.set('runtime', 'installer', "1")
  
if args.contourlines:
  if os.path.exists("styles/contourlines_style") == True:
    contourlines.create_cont()
  else:
    printwarning("dir styles/contourlines_style not found")
 
config.read('pygmap3.cfg')

if args.stop_after == "contourlines":
  print()
  printinfo("stop after contourlines creation")
  print()
  quit()


"""
mapdata to use

if --keep_data is set, then use the old data

"""

os.chdir(WORK_DIR)

if args.keep_data == False:
  
  if os.path.exists("o5m/" + buildmap + ".o5m") == False:
    mapdata.create_o5m()
  
  """
  update mapdata

  """
  if args.hourly:
    config.set('runtime', 'hourly', '1')

  if args.minutely:
    config.set('runtime', 'minutely', '1')
    
  write_config()
  
  mapdata.update_o5m()

"""
--stop_after mapdata

"""

config.read('pygmap3.cfg')
if args.stop_after == "mapdata":
  print()
  printinfo(" Mapdata for " + buildmap + " " + config['time_stamp'][buildmap] + " successful extracted/updated")
  print()
  quit()


"""
split mapdata

"""

def remove_old_tiles():
  path = 'tiles'
  for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
      try:
        os.remove(os.path.join(path, file))
      except:
        print('Could not delete', file, 'in', path)

if args.no_split:
  if os.path.exists(WORK_DIR + "tiles/" + buildmap + "_split.ready") == False:
    print()
    printwarning("can't find tiles/" + buildmap + "_split.ready")
    print("--no_split/-ns makes no sense, ignoring it")
    splitter.split()

else:
  remove_old_tiles()
  os.chdir(WORK_DIR)
  print()
  printinfo("now splitting the mapdata...")
  splitter.split()

"""
--stop_after splitter

"""

config.read('pygmap3.cfg')
if args.stop_after == "splitter":
  print()
  printinfo(buildmap + ".o5m successful splitted")
  print()
  quit()

"""
render the map-images

"""

mkgmap.render()

  
"""
--stop_after mkgmap

"""

if args.stop_after == "mkgmap":
  config.read('pygmap3.cfg')
  print()
  printinfo(" Mapset for " + buildmap + " successful created")
  print()
  quit()

"""
zip the images, save the kml and log

"""

if args.zip_img:
  store.zip_img()
  store.kml()

if args.log:
  store.log()

today = datetime.datetime.now()
DATE = today.strftime('%Y%m%d_%H%M')

config.read('pygmap3.cfg')

print()
print()
print(" ----- " + (DATE) + " ----- " + (buildmap) + " ready! -----")
print()
print()


quit()


