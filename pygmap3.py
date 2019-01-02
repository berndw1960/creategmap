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


import os
import datetime
import argparse
import configparser
import shutil

import build_config
import get_tools
import precomp
import geonames
import contourlines
import mapdata
import splitter
import mkgmap
import store


__version__ = "0.9.50"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2018 Bernd Weigelt"
__credits__ = "Franco B."
__license__ = "AGPLv3"
__maintainer__ = "Bernd Weigelt"
__email__ = "weigelt.bernd@web.de"
__status__ = "RC"


WORK_DIR = os.environ['HOME'] + "/map_build/"


# set prefix for messages
def info(msg):
    print("II: " + msg)


def warn(msg):
    print("WW: " + msg)


def error(msg):
    print("EE: " + msg)


if not os.path.exists(WORK_DIR):
    print()
    error("Please create " + WORK_DIR)
    print()
    quit()


os.chdir(WORK_DIR)


if os.path.exists("pygmap3.cfg"):
    if os.path.exists("pygmap3.cfg.bak"):
        os.remove("pygmap3.cfg.bak")

    shutil.copyfile('pygmap3.cfg', 'pygmap3.cfg.bak')


# create dir o5m, poly and tiles
for dir in ['o5m', 'poly', 'tiles', 'precomp']:
    if not os.path.exists(dir):
        os.mkdir(dir)


# configparser
def write_config():
    with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)


config = configparser.ConfigParser()


# create a new config if needed
if not os.path.exists("pygmap3.cfg"):
    build_config.create()


build_config.update()


config.read('pygmap3.cfg')


# argparse
parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\

            To build maps for Garmin PNA

            map layers (routable):
            basemap - to route motorvehicle, bicycle and pedestrian
            bikemap - better visibility of cycleroutes and -ways
            carmap  - only for motorvehicle, no special routing
            for bicycle and pedestrian

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
parser.add_argument('-xmx', '--xmx', default=config['java']['xmx'],
                    help=" set the HEAP for Java, min. 500 MB per thread," +
                         " an example '6G' or '6000M' for a CPU with 4 cores" +
                         " and 8 threads. ")
parser.add_argument('-xms', '--xms', default=config['java']['xms'],
                    help=" set the HEAP, could be the same value as -Xmx," +
                         " but a different value is possible ")
parser.add_argument('-agh', '--aggressiveheap', action="store_true",
                    help=" set the HEAP permanent in an aggressive mode")
parser.add_argument('-no_agh', '--no_aggressiveheap', action="store_true",
                    help=" disable the aggressive mode ")

# interactive mode
parser.add_argument('-i', '--interactive', action="store_true",
                    help=" an interactive mode to set the region")

# edit options interactive
parser.add_argument('-e', '--edit_opts', default=0,
                    help=" list and edit the options for the maps")
parser.add_argument('-et', '--edit_template', action="store_true",
                    help=" list and edit the template for the options")

# mapset handling
parser.add_argument('-r', '--region', default=0,
                    help=" set the map region to build " +
                         " need at least a poly or a O5M file ")
parser.add_argument('-p', '--poly', default=0,
                    help=" set the poly file for the map region to build")
parser.add_argument('-lp',  '--list_poly', action="store_true",
                    help="list all poly files in " + WORK_DIR + "poly ")
parser.add_argument('-o', '--o5m', default=0,
                    help=" set the o5m file for the map region to build")
parser.add_argument('-lo', '--list_o5m', action="store_true",
                    help=" list all O5M files in " + WORK_DIR + "o5m ")
parser.add_argument('-s', '--set_default', default=0,
                    help="set region to build as new default")

# mapstyle handling
parser.add_argument('-lm', '--list_mapstyle', action="store_true",
                    help="list the style settings")
parser.add_argument('-as', '--add_style', default=0,
                    help="add a new style")
parser.add_argument('-rs', '--rm_style', default=0,
                    help="remove a style")

# mapdata
parser.add_argument('-k', '--keep_data', action="store_true",
                    help="don't update the mapdata")
parser.add_argument('-nb', '--new_bounds', action="store_true",
                    help="try to get precomp sea or bounds")
parser.add_argument('-ub', '--use_bounds', default=0,
                    help="use a special bounds file")
parser.add_argument('-us', '--use_sea', default=0,
                    help="use a special sea file")
parser.add_argument('-lb', '--list_bounds', action="store_true",
                    help="list the local precomp sea or bounds")
parser.add_argument('-rb', '--reset_bounds', action="store_true",
                    help="use the latest precomp sea or bounds")
parser.add_argument('--hourly', action="store_true",
                    help="update the raw mapdata with the hourly files")
parser.add_argument('--minutely', action="store_true",
                    help="update the raw mapdata with the minutely files")

# splitter options
parser.add_argument('-ns', '--no_split', action="store_true",
                    help="don't split the mapdata")
parser.add_argument('-mn', '--maxnodes',
                    help="set the maxnodes for splitter")

# mkgmap options
parser.add_argument('-mj', '--max_jobs', default='yes',
                    help=" set the used threads to use with mkgmap")
parser.add_argument('-kg', '--keep_going', action="store_true",
                    help=False)
parser.add_argument('-in', '--installer', action="store_true",
                    help="create mapsource installer")

# editable with commandline options
parser.add_argument('-lv', '--levels', default=config['maplevel']['levels'],
                    help="This is a number between 0 and 16")
parser.add_argument('-dd', '--dem_dists', default=config['demtdb']['demdists'],
                    help="set the distance between two points")
parser.add_argument('-c', '--contourlines', action="store_true",
                    help=False)
parser.add_argument('-edu', '--ed_user', default=0,
                    help=False)
parser.add_argument('-edp', '--ed_pwd', default=0,
                    help=False)

# image handling
parser.add_argument('-z', '--zip_img', action="store_true",
                    help=False)

# debugging
parser.add_argument('-cs', '--check_styles', action="store_true",
                    help=False)
parser.add_argument('-st', '--stop_after', default=0,
                    help='[get_tools|contourlines|mapdata|splitter|mkgmap]')
parser.add_argument('-so', '--spec_opts', action="store_true",
                    help="use some special opts to test the raw data")
parser.add_argument('-v', '--verbose', action="store_true",
                    help=False)
parser.add_argument('-l', '--log', action="store_true",
                    help=False)

# development
parser.add_argument('-lt', '--list_test_version', action="store_true",
                    help="list the test versions of splitter and mkgmap")
parser.add_argument('-spt', '--splitter_test', default=0,
                    help="use a svn version of splitter")
parser.add_argument('-mt', '--mkgmap_test', default=0,
                    help="use a svn version of mkgmap")

args = parser.parse_args()


# list the poly files
if args.list_poly:
    path = WORK_DIR + "poly"
    dir = sorted(os.listdir(path))
    print()
    info(" This poly files are in '" + WORK_DIR + "poly': ")
    print()
    for file in dir:
        file = os.path.splitext(file)[0]
        print(file)
    print()
    quit()


# list the O5M files
if args.list_o5m:
    path = WORK_DIR + "o5m"
    dir = sorted(os.listdir(path))
    print()
    info(" This O5M files are in '" + WORK_DIR + "o5m': ")
    print()
    for file in dir:
        file = os.path.splitext(file)[0]
        print(file)
    print()
    quit()


# set default buildmap
if args.set_default or not config.has_option('runtime', 'default'):
    buildmap = input(" \n\n " +
                     "    Which should be your default map region? \n" +
                     "    You can build this region without any option\n" +
                     "    for pygmap3.py in the future.\n\n" +
                     "    please enter a region:    ")
    buildmap = os.path.splitext(buildmap)[0]
    config.set('runtime', 'default', buildmap)
    write_config()


# set the buildmap
if args.interactive:
    buildmap = input(" \n\n" +
                     "    Which map region should be build? \n\n" +
                     "    please enter a region:    ")
elif args.region:
    buildmap = args.region
elif args.edit_opts:
    buildmap = args.edit_opts
elif args.poly:
    print()
    warn("The option -p/--poly will be removed in further releases,\n" +
         "    please use -r/--region instead")
    buildmap = args.poly
elif args.o5m:
    print()
    warn("The option -o/--o5m will be removed in further releases,\n" +
         "    please use -r/--region instead")
    buildmap = args.o5m
else:
    buildmap = config['runtime']['default']


buildmap = os.path.splitext(buildmap)[0]
config.set('runtime', 'buildmap', buildmap)


if not config.has_section(buildmap):
    config.add_section(buildmap)
    for key in config['map_styles']:
        config.set(buildmap, key, config['map_styles'][key])
        print_warn = "1"
    config.set(buildmap, 'name_tag_list', config['name_tag_list']['default'])
    print_warn = "1"
    write_config()
    text = ("Some options are set to default values\n" +
            "    you can edit them with pygmap3.py -e")
    if print_warn == "1":
        print()
        warn(text)
        question = ("\n Do you want to edit the configuration? [y|N]   ")
        want_edit = input(question)
        if want_edit == "y":
            print()
            info("please use 'pygmap3.py -e " + buildmap + "'")
            print()
            quit()


# move old name_tag_list entries to buildmap options
if config.has_option('name_tag_list', buildmap):
    ntl_temp = config['name_tag_list'][buildmap]
    config.set(buildmap, 'name_tag_list', ntl_temp)
    config.remove_option('name_tag_list', buildmap)


for style in config['map_styles']:
    if not config.has_option(buildmap, style):
        config.set(buildmap, style, config['map_styles'][style])
        write_config()


if args.edit_opts:
    print()
    info("Options for the region '" + buildmap + "':\n")
    for key in config[buildmap]:
        print("    " + key + "    " + config[buildmap][key])
    print()
    text = ("    Should this options be edited? [y|N|a|d]    ")
    edit = input(text)
    if edit == "y":
        print("\n to end editing set a value to 'q'\n\n")
        finish = "no"
        while finish == "no":
            text = ("  Add the key to edit:   ")
            new_key = input(text)
            if new_key != "name_tag_list":
                text = ("  Add the new value:     ")
                new_value = input(text)
                if new_value == 'q':
                    finish = "yes"
                else:
                    config.set(buildmap, new_key, new_value)
            else:
                if config.has_option(buildmap, 'name_tag_list'):
                    print()
                    info("this is the name tag list in the config file")
                    print()
                    print("    " + buildmap + " --> " +
                          config[buildmap]['name_tag_list'])
                text = (" \n\n" +
                        "    Which language do you prefer for naming \n" +
                        "    objects in your map?\n\n " +
                        "   'name:en,name:int,name' is the english value,\n" +
                        "    you can use german, french, dutch or spanish\n" +
                        "    press 'Enter' for the default english value\n\n" +
                        "    please enter a language:   ")
                language = input(text)
                if language == "german":
                    name_tag_list = 'name:de,name:int,name'
                elif language == "french":
                    name_tag_list = 'name:fr,name:int,name'
                elif language == "dutch":
                    name_tag_list = 'name:nl,name:int,name'
                elif language == "spanish":
                    name_tag_list = 'name:es,name:int,name'
                else:
                    name_tag_list = 'name:en,name:int,name'
                config.set(buildmap, 'name_tag_list', name_tag_list)
            write_config()
    elif edit == "a":
        print("\n to end editing set a value to 'q'\n\n")
        finish = "no"
        while finish == "no":
            text = ("Add the new key:   ")
            new_key = input(text)
            text = ("Add the new value:   ")
            new_value = input(text)
            if new_value == "q":
                finish = "yes"
            else:
                config.set(buildmap, new_key, new_value)
        write_config()
    elif edit == "d":
        text = ("Really delete the options for '" + buildmap + "'? [y|N]   ")
        kill_opts = input(text)
        if kill_opts == "y":
            for key in config[buildmap]:
                config.remove_option(key)
            config.remove_section(buildmap)
            write_config()
            print()
            quit()
            print()
    print()
    info("These are the new values in section " +
         buildmap + ":\n\n")
    for key in config[buildmap]:
        print("    " + key + "  " + config[buildmap][key])
    print()
    quit()


if args.edit_template:
    print()
    print("\n\n" +
          "  These are the template options:\n")
    for key in config['template_region']:
        print("    " + key + "    " + config['template_region'][key])
    print()
    text = ("    Should this options be edited? [y|N|a|d]    ")
    edit = input(text)
    if edit == "y":
        print("\n to end editing set a value to 'q'\n\n")
        finish = "no"
        while finish == "no":
            text = ("  Add the key to edit:   ")
            new_key = input(text)
            text = ("  Add the new value:     ")
            new_value = input(text)
            if new_value == 'q':
                finish = "yes"
            else:
                config.set('template_region', new_key, new_value)
    elif edit == "a":
        print("\n to end editing set a value to 'q'\n\n")
        finish = "no"
        while finish == "no":
            text = ("  Add the new key:   ")
            new_key = input(text)
            text = ("  Add the new value:   ")
            new_value = input(text)
            if new_value == 'q':
                finish = "yes"
            else:
                config.set('template_region', new_key, new_value)
    elif edit == "d":
        print("\n to finish hit 'q'\n\n")
        finish = "no"
        while finish == "no":
            text = ("  which key should be deleted?   ")
            del_key = input(text)
            if del_key == 'q':
                finish = "yes"
            else:
                text = ("    Really delete this'" + del_key + "'? [y|N]   ")
                kill_key = input(text)
                if kill_key == "y":
                    config.remove_option('template_region', del_key)
    write_config()
    print()
    quit()


# map build options
if args.list_mapstyle:
    if config.has_section('map_styles'):
        print()
        info("map_styles list includes: ")
        print()
        for key in config['map_styles']:
            print("  " + key)
        print()
        if config.has_section('mapset'):
            print()
            info("mapset list includes: ")
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


def info_styles():
    print()
    error(args.add_style + "_style - dir not found")
    print()
    info("possible styles for routable layers are: ")
    print("    basemap")
    print("    bikemap")
    print("    carmap")
    print("    olddev")
    print("    defaultmap")
    print()
    info("possible styles as overlays are:")
    print("    bikeroute")
    print("    boundary")
    print("    fixme")
    print()
    print("    or your own style files!")
    print()


if args.add_style:
    if os.path.exists("styles/" + args.add_style + "_style"):
        if args.add_style not in config:
            print()
            info("please add a section [" + args.add_style + "] ")
            print(" to pygmap3.cfg")
            print(" see the existing entries for the fixme layer as example")
            print(" for family-id and product-id increase the values")
            print(" mapid_ext and draw_priority could be the same values")
            print(" family_name is a free text value")
            print()
            info("please read mkgmap's manual for more infos")
            print()
            print("  [fixme]")
            for key in config['fixme']:
                print("  " + key + " = " + config['fixme'][key])
            print()
        config.set('map_styles', args.add_style, '1')

    elif args.add_style == "defaultmap":
        config.set('map_styles', args.add_style, '1')
    else:
        info_styles()
        quit()
    write_config()
    quit()


if args.rm_style:
    if config.has_option('map_styles', args.rm_style):
        config.remove_option('map_styles', args.rm_style)
        write_config()
    quit()


# set or create the mapid
if config.has_option(buildmap, 'mapid'):
    mapid = config[buildmap]['mapid']
else:
    mapid = config['mapid']['next_mapid']
    next_mapid = str(int(mapid)+1)
    config.set(buildmap, 'mapid',  mapid)
    config.set('mapid', 'next_mapid', next_mapid)


write_config()


if args.check_styles:
    mkgmap.check()
    quit()


# special opts to debug the raw map data
if args.spec_opts:
    config.set('runtime', 'use_spec_opts', '1')


# logging
if args.log:
    config.set('runtime', 'logging', '1')


# verbosity
if args.verbose:
    config.set('runtime', 'verbose', '1')


# HEAP size for java, default is aggressiveheap
if args.aggressiveheap:
    config.set('java', 'agh', '1')


if args.no_aggressiveheap:
    config.set('java', 'agh', '0')


if config['java']['agh'] == "0":
    if args.xmx != config['java']['xmx']:
        config.set('java', 'xmx', "-Xmx" + str(args.xmx))
    if args.xms != config['java']['xms']:
        config.set('java', 'xms', "-Xms" + str(args.xms))


# maxnodes for splitter
if args.maxnodes and args.maxnodes != config['maxnodes']['default']:
    config.set('maxnodes', buildmap, args.maxnodes)
elif args.maxnodes and args.maxnodes == config['maxnodes']['default']:
    config.remove_option('maxnodes', buildmap)


# development version of splitter and mkgmap
if args.list_test_version:
    get_tools.list_test_version()
    quit()


if args.splitter_test:
    config.set('splitter', 'test', args.splitter_test)
    print()
    info(" SPLITTER test version set to " + args.splitter_test)


if args.mkgmap_test:
    config.set('mkgmap', 'test', args.mkgmap_test)
    print()
    info(" MKGMAP test version set to " + args.mkgmap_test)


# set the amount of levels
if args.levels != config['maplevel']['levels']:
    config.set('maplevel', 'levels', args.levels)


# max-jobs for mkgmap
if args.max_jobs:
    config.set('runtime', 'max_jobs', args.max_jobs)


# keep_going on errors
if args.keep_going:
    config.set('runtime', 'keep_going', "1")


if args.dem_dists != config['demtdb']['demdists']:
    config.set('demtdb', 'demdists', args.dem_dists)


if args.ed_user:
    config.set('runtime', 'ed_user', args.ed_user)


if args.ed_pwd:
    config.set('runtime', 'ed_pwd', args.ed_pwd)


write_config()


# osmupdate and osmconvert
if config['osmtools']['check'] == "yes":
    def checkprg(programmtofind, solutionhint):
        if os.system("which " + programmtofind) == 0:
            print()
            info(programmtofind + " found")
        else:
            print()
            error(programmtofind + " not found")
            print(solutionhint)
            quit()

    for tool in ['osmconvert', 'osmupdate']:
        hint = (tool + " missed, please use mk_osmtools " +
                       "to build it from sources")
        print()
        checkprg(tool, hint)

    config.set('osmtools', 'check', 'no')
    write_config()


# get splitter and mkgmap
get_tools.get_tools()

config.read('pygmap3.cfg')


# get the geonames file
geonames.cities15000()


# bounds and precomp_sea
if args.list_bounds:
    precomp.list_bounds()
    quit()


if args.reset_bounds:
    config.set('precomp', 'bounds', "bounds-latest.zip")
    config.set('precomp', 'sea', "sea-latest.zip")
    write_config()
    quit()


if args.new_bounds:
    os.chdir(WORK_DIR + "precomp")
    for i in ['sea', 'bounds']:
        if os.path.exists(i + "-latest.zip"):
            os.remove(i + "-latest.zip")
    config.set('precomp', 'bounds', "bounds-latest.zip")
    config.set('precomp', 'sea', "sea-latest.zip")
    os.chdir(WORK_DIR)
    quit()


if args.use_bounds:
    config.set('precomp', 'bounds', args.use_bounds)


if args.use_sea:
    config.set('precomp', 'sea', args.use_sea)


write_config()


precomp.fetch_bounds()


# --stop_after get_tools
config.read('pygmap3.cfg')
if args.stop_after == "get_tools":
    print()
    info("needed programs found and files successfully loaded")
    print()
    quit()


# create an installer for mapsource
if args.installer:
    config.set('runtime', 'installer', "1")


if args.contourlines:
    if os.path.exists("styles/contourlines_style"):
        contourlines.create_cont()
    else:
        warn("dir styles/contourlines_style not found")


# --stop_after contourlines
config.read('pygmap3.cfg')
if args.stop_after == "contourlines":
    print()
    info("stop after contourlines creation")
    print()
    quit()


# mapdata to use
os.chdir(WORK_DIR)

if not args.keep_data:
    if not os.path.exists("o5m/" + buildmap + ".o5m"):
        mapdata.create_o5m()

    # update mapdata
    if args.hourly:
        config.set('runtime', 'hourly', '1')

    if args.minutely:
        config.set('runtime', 'minutely', '1')

    write_config()

    mapdata.update_o5m()


# --stop_after mapdata
config.read('pygmap3.cfg')
if args.stop_after == "mapdata":
    print()
    info(" Mapdata for " + buildmap + " " +
         config['time_stamp'][buildmap] +
         " successful extracted/updated")
    print()
    quit()


# split mapdata
def remove_old_tiles():
    path = 'tiles'
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            os.remove(os.path.join(path, file))


if args.no_split:
    if not os.path.exists(WORK_DIR + "tiles/" + buildmap + "_split.ready"):
        print()
        warn("can't find tiles/" + buildmap + "_split.ready")
        print("--no_split/-ns makes no sense, ignoring it")
        splitter.split()
else:
    remove_old_tiles()
    os.chdir(WORK_DIR)
    print()
    info("now splitting the mapdata...")
    splitter.split()


# --stop_after splitter
config.read('pygmap3.cfg')
if args.stop_after == "splitter":
    print()
    info(buildmap + ".o5m successful splitted")
    print()
    quit()


# render the map-images
mkgmap.render()


# --stop_after mkgmap
if args.stop_after == "mkgmap":
    config.read('pygmap3.cfg')
    print()
    info(" Mapset for " + buildmap + " successful created")
    print()
    quit()


# zip the images, save the kml and log
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
