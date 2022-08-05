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


__version__ = "1.0.0"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2020 Bernd Weigelt"
__credits__ = "Franco B."
__license__ = "AGPLv3"
__maintainer__ = "Bernd Weigelt"
__email__ = "weigelt.bernd@web.de"
__status__ = "released"


WORK_DIR = os.path.expanduser('~') + "/map_build/"


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


#if os.path.isfile("pygmap3.lck"):
#    os.remove("pygmap3.lck")
#    print()
#    error("last run of pygmap3.py was not ended correctly!\n\n")
#    quit()
#else:
#    fobj = open("pygmap3.lck", "w")
#    fobj.close()


if os.path.isfile("pygmap3.cfg"):
    if os.path.isfile("pygmap3.cfg.bak"):
        os.remove("pygmap3.cfg.bak")

    shutil.copyfile('pygmap3.cfg', 'pygmap3.cfg.bak')


# create dir o5m, poly and tiles
for dir in ['o5m', 'pbf', 'poly', 'tiles', 'precomp']:
    if not os.path.exists(dir):
        os.mkdir(dir)


# configparser
def write_config():
    with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)


config = configparser.ConfigParser()


# create a new config if needed
if not os.path.isfile("pygmap3.cfg"):
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
                    help=" set the HEAP for Java, min. 500 MB per thread,"
                         + " '4G' or '4000M' for a CPU with 4 cores"
                         + " and 8 threads. ")
parser.add_argument('-xms', '--xms', default=config['java']['xms'],
                    help=" set the HEAP, could be the same value as -Xmx,"
                         + " but a different value is possible ")
parser.add_argument('-agh', '--aggressiveheap', action="store_true",
                    help=" set the HEAP permanent in an aggressive mode")
parser.add_argument('-no_agh', '--no_aggressiveheap', action="store_true",
                    help=" disable the aggressive mode ")

# interactive mode
parser.add_argument('-i', '--interactive', action="store_true",
                    help=" an interactive mode to set the region")

# edit options interactive
parser.add_argument('-lr', '--list_regions', action="store_true",
                    help=" list the sections in configuration")
parser.add_argument('-e', '--edit_opts', action="store_true",
                    help=" edit the regions in configuration")

# mapset handling
parser.add_argument('-r', '--region', default=0,
                    help=" set the map region to build " +
                         " need at least a poly or a O5M file ")
parser.add_argument('-lp',  '--list_poly', action="store_true",
                    help="list all poly files in " + WORK_DIR + "poly ")
parser.add_argument('-lo', '--list_o5m', action="store_true",
                    help=" list all O5M files in " + WORK_DIR + "o5m ")
parser.add_argument('-uo', '--update_o5m', action="store_true",
                    help="update all local o5m files")
parser.add_argument('-s', '--set_default', action="store_true",
                    help="set region to build as new default")

# mapstyle handling
parser.add_argument('-lm', '--list_mapstyle', action="store_true",
                    help="list the style settings")
parser.add_argument('-as', '--add_style', default=0,
                    help="add a new style")
parser.add_argument('-rs', '--rm_style', default=0,
                    help="remove a style")

# update tools
parser.add_argument('-kt', '--keep_tools', action="store_true",
                    help="don't update the tools from mkgmap")

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
parser.add_argument('-nps', '--no_sea', action="store_true",
                    help="don't use precompiled sea tiles")
parser.add_argument('-npb', '--no_bounds', action="store_true",
                    help="don't use precompiled bounds")
parser.add_argument('--hourly', action="store_true",
                    help="update the raw mapdata with the hourly files")
parser.add_argument('--minutely', action="store_true",
                    help="update the raw mapdata with the minutely files")

# splitter options
parser.add_argument('-ns', '--no_split', action="store_true",
                    help="don't split the mapdata")
parser.add_argument('-mn', '--maxnodes',
                    help="set the maxnodes for splitter")
parser.add_argument('-spv', '--splitter_version', default=0,
                    help="splitter version to use, use it with '-spv r123'")

# mkgmap options
parser.add_argument('-mj', '--max_jobs', default='yes',
                    help=" set the used threads to use with mkgmap")
parser.add_argument('-kg', '--keep_going', action="store_true",
                    help=False)
parser.add_argument('-in', '--installer', action="store_true",
                    help="create mapsource installer")
parser.add_argument('-mkv', '--mkgmap_version', default=0,
                    help="mkgmap version to use, use it with '-mkv r123'")

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
    info("This poly files are in '" + WORK_DIR + "poly': ")
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
    info("This O5M files are in '" + WORK_DIR + "o5m': ")
    print()
    for file in dir:
        file = os.path.splitext(file)[0]
        print(file)
    print()
    quit()


# update all local o5m files and quit
if args.update_o5m:
    path = WORK_DIR + "o5m"
    dir = sorted(os.listdir(path))
    for o5m in dir:
        o5m = os.path.splitext(o5m)[0]
        config.set('runtime', 'region', o5m)
        write_config()
        mapdata.update_o5m()
    print()
    info("All o5m files successful updated")
    print()
    quit()


if args.list_regions or args.edit_opts:
    print()
    pre_region_list = []
    new_region_list = []
    print_new_list = "no"
    for section in config.sections():
        if config.has_option(section, 'new_region'):
            print_new_list = "yes"
            new_region_list.append(section)
        elif config.has_option(section, 'mapid'):
            pre_region_list.append(section)
    print()
    if print_new_list == "yes":
        info("These are new regions with default values:\n")
        for key in new_region_list:
            print("    " + key)
        print()
        print()
    info("These are configured regions:\n")
    for key in pre_region_list:
        print("    " + key)
    print()


if args.list_regions:
    quit()


# set default region
if args.set_default or not config.has_option('runtime', 'default_region'):
    region = input(" \n\n"
                   + "    Which should be your default map region? \n"
                   + "    You can build this region without any option\n"
                   + "    for pygmap3.py in the future.\n\n"
                   + "    please enter a region:    ")
    region = os.path.splitext(region)[0]
    config.set('runtime', 'default_region', region)
    write_config()


# set the region
if args.interactive:
    region = input(" \n\n"
                   + "    Which map region should be build? \n\n"
                   + "    please enter a region:    ")
elif args.region:
    region = args.region
else:
    region = config['runtime']['default_region']


region = os.path.splitext(region)[0]
config.set('runtime', 'region', region)


if not config.has_section(region):
    config.add_section(region)
    config.set(region, 'new_region', 'yes')


for section in config.sections():
    if config.has_option(section, 'new_region'):
        for key in config['mapstyles']:
            config.set(section, key, config['mapstyles'][key])
        config.set(section, 'name_tag_list',
                   config['name_tag_list']['default'])
        # copy style config to new regions
        for style in config['mapstyles']:
            if (not config.has_option(section, style) and
               not config.has_option(section, 'lock')):
                config.set(section, style, config['mapstyles'][style])
            if not config.has_option('template_region', style):
                config.set('template_region', style,
                           config['mapstyles'][style])
        # set the mapid to new regions
        mapid = config['mapid']['next_mapid']
        next_mapid = str(int(mapid)+1)
        config.set(section, 'mapid',  mapid)
        config.set('mapid', 'next_mapid', next_mapid)
        config.remove_option(section, 'new_region')

write_config()


if args.edit_opts:
    for folder in [WORK_DIR + "hgt/COPERNICUS",
                   WORK_DIR + "hgt/VIEW1",
                   WORK_DIR + "hgt/VIEW3"]:
        if os.path.exists(folder):
            hillshading = '1'

    print()
    info("You can edit these regions\n"
         + "     or enter a name for a new region\n ")
    text_new_section = "    Add the new region:   "
    text_new_key = "    Add the new key:   "
    text_new_value = "    Add the new value:   "
    text_end = "\n    to end editing set a key to 'q'"
    text_ntl = (" \n"
                + "    Which language do you prefer for naming \n"
                + "    objects in your map?\n\n "
                + "    default is the english value,\n\n"
                + "    'name:en,name:int,name'\n\n"
                + "    you can also use:\n\n"
                + "    de --> german\n"
                + "    fr --> french\n"
                + "    nl --> dutch\n"
                + "    es --> spanish\n"
                + "    it --> italian\n"
                + "    or other by enter the ISO Code\n\n"
                + "    press 'Enter' for the default english value\n\n"
                + "    'q' breaks without changings\n\n"
                + "    please enter only a ISO code:   ")

    text = ("\n    Please enter the name of the region:\n\n"
            + "    Enter the name, 'q' to exit: ")
    opts_region = input(text)
    if opts_region == "q":
        print()
        quit()

    my_list = []
    if config.has_section(opts_region):
        print()
        info("Options in section '" + opts_region + "':\n")
        for key in config[opts_region]:
            my_list.append(key)
        for key in my_list:
            print("    " + str(my_list.index(key)+1) + "\t"
                  + key + "\n\t\t\t" + config[opts_region][key])
        text = ("\n\n    You can edit, add and delete sections "
                + "and options in pygmap3.cfg. \n\n"
                + "    [e]dit | [a]dd | [d]elete | [q]uit \n\n"
                + "    Enter your choice:    ")
        edit = input(text)
    else:
        print()
        warn("This is a new region, please at least one key.\n"
             + "    see the section [template_region] as example")
        my_list = []
        print()
        info("Options in section [template_region]:\n")
        for key in config['template_region']:
            my_list.append(key)
        for key in my_list:
            print("    " + str(my_list.index(key)+1) + "     "
                  + key + "    " + config['template_region'][key])
        edit = "a"

    if edit == "q":
        print()
        quit()
    elif edit == "e":
        print(text_end)
        fin = "no"
        while fin != "q":
            print()
            text = "    Enter the number of the key to edit:   "
            num_key = input(text)
            if num_key == "q":
                break
            new_key = int(num_key)-1
            new_key = my_list[new_key]
            if new_key != "name_tag_list":
                if new_key in config['tdb_layer'] and hillshading == '1':
                    print()
                    info(" If you want to enable hillshading for this layer,"
                         + "\n     set it to 'tdb' instead of ' yes'!")
                print("\n    Old value:   " + new_key
                      + " = " + config[opts_region][new_key] + "\n")
                text = text_new_value
                new_value = input(text)
                if new_value != config[opts_region][new_key]:
                    config.set(opts_region, new_key, new_value)
                    write_config()
            else:
                language = input(text_ntl)
                if language == "q":
                    break
                elif language:
                    name_tag_list = "name:" + language + ",name:int,name"
                else:
                    name_tag_list = 'name:en,name:int,name'
                config.set(opts_region, 'name_tag_list', name_tag_list)
            if config.has_option(opts_region, 'new_region'):
                config.remove_option(opts_region, 'new_region')
                write_config()
    elif edit == "a":
        if not config.has_section(opts_region):
            config.add_section(opts_region)

        text = ("\n    Which options do want to add"
                + " to pygmap3.cfg?\n\n")
        print(text_end)
        fin = "no"
        while fin != "q":
            print()
            text = text_new_key
            new_key = input(text)
            if new_key == "q":
                break

            if new_key != "name_tag_list":
                text = text_new_value
                new_value = input(text)
                config.set(opts_region, new_key, new_value)
            else:
                language = input(text_ntl)
                if language == "q":
                    break
                elif language:
                    name_tag_list = "name:" + language + ",name:int,name"
                else:
                    name_tag_list = 'name:en,name:int,name'
                config.set(opts_region, 'name_tag_list', name_tag_list)

    elif edit == "d":
        text = ("\n    You can delete [a]ll, [s]ome or [N]o option\n"
                + "    Use [q] to exit without changes. \n\n"
                + "    Enter your choice:  ")
        kill_opts = input(text)
        if kill_opts == "q":
            quit()
        elif kill_opts == "a":
            text = ("    Really delete ALL options for '"
                    + opts_region + "'? [y|N]   ")
            rem_section = input(text)
            if rem_section == "y":
                config.remove_section(opts_region)
                write_config()
                print("\n    " + opts_region + " removed!\n")
                quit()
            else:
                print()
                quit()
        elif kill_opts == "s":
            print(text_end)
            fin = "no"
            while fin != "q":
                print()
                text = "    Enter the number of the key to delete:   "
                rem_option = input(text)
                if rem_option == "q":
                    break
                rem_option = int(rem_option)-1
                rem_option = my_list[rem_option]
                config.remove_option(opts_region, rem_option)

    write_config()
    print()
    info("These are the new values for the region "
         + opts_region + ":\n")
    for key in config[opts_region]:
        print("    " + key + "\n\t\t\t" + config[opts_region][key])
    print()
    quit()


# map build options
if args.list_mapstyle:
    if config.has_section('mapstyles'):
        print()
        info("mapstyles list includes: ")
        print()
        for key in config['mapstyles']:
            print("  " + key)
        print()
        if config.has_section('mapset'):
            print()
            info("mapset list includes: ")
            if config.has_option('runtime', 'default_region'):
                print()
                print(" default:")
                print("  " + config['runtime']['default_region'])
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
        config.set('mapstyles', args.add_style, 'no')

    elif args.add_style == "defaultmap":
        config.set('mapstyles', args.add_style, 'no')
    else:
        info_styles()
        quit()
    write_config()
    quit()


if args.rm_style:
    if config.has_option('mapstyles', args.rm_style):
        config.remove_option('mapstyles', args.rm_style)
        write_config()
    quit()


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


if args.xmx:
    if args.xmx != config['java']['xmx']:
        config.set('java', 'xmx', "-Xmx" + str(args.xmx))


if args.xms:
    if args.xms != config['java']['xms']:
        config.set('java', 'xms', "-Xms" + str(args.xms))


# maxnodes for splitter
if args.maxnodes and args.maxnodes != config['maxnodes']['default']:
    config.set('maxnodes', region, args.maxnodes)
elif args.maxnodes and args.maxnodes == config['maxnodes']['default']:
    config.remove_option('maxnodes', region)


# development version of splitter and mkgmap
if args.list_test_version:
    get_tools.list_test_version()
    quit()


if args.splitter_test:
    config.set('splitter', 'test', args.splitter_test)
    print()
    info("SPLITTER test version set to " + args.splitter_test)


if args.mkgmap_test:
    config.set('mkgmap', 'test', args.mkgmap_test)
    print()
    info("MKGMAP test version set to " + args.mkgmap_test)


# to use previous versions of splitter and mkgmap
if args.splitter_version:
    config.set('splitter', 'old_version', '1')
    config.set('splitter', 'rev', 'splitter-' + args.splitter_version)
    write_config()
    print()
    info("SPLITTER version set to " + config['splitter']['rev'])


if args.mkgmap_version:
    config.set('mkgmap', 'old_version', '1')
    config.set('mkgmap', 'rev', 'mkgmap-' + args.mkgmap_version)
    write_config()
    print()
    info("MKGMAP version set to " + config['mkgmap']['rev'])


if args.keep_tools:
    config.set('splitter', 'old_version', '1')
    print()
    info("SPLITTER version set to " + config['splitter']['rev'])

    config.set('mkgmap', 'old_version', '1')
    print()
    info("MKGMAP version set to " + config['mkgmap']['rev'])


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
    config.set('earthdata', 'ed_user', args.ed_user)


if args.ed_pwd:
    config.set('earthdata', 'ed_pwd', args.ed_pwd)


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
        hint = (tool + " missed, please use mk_osmtools "
                       + "to build it from sources")
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
    precomp.fetch_bounds()
    print()
    quit()


if args.use_bounds:
    config.set('precomp', 'bounds', args.use_bounds)


if args.use_sea:
    config.set('precomp', 'sea', args.use_sea)


if args.no_sea:
    config.set('runtime', 'no_sea', '1')


if args.no_bounds:
    config.set('runtime', 'no_bounds', '1')


write_config()





# check bounds, download only if needed
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
    if not os.path.exists("o5m/" + region + ".o5m"):
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
    info("Mapdata for " + region + " successful extracted/updated")
    print()
    quit()


# split mapdata
def remove_old_tiles():
    path = 'tiles'
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            os.remove(os.path.join(path, file))


if args.no_split:
    if not os.path.exists(WORK_DIR + "tiles/" + region + "_split.ready"):
        print()
        warn("can't find tiles/" + region + "_split.ready")
        print("--no_split/-ns makes no sense, ignoring it")
        splitter.split()
else:
    remove_old_tiles()
    os.chdir(WORK_DIR)
    print()
    info("now splitting the mapdata...")
    splitter.split()


#  remove test option
if config.has_option('splitter', 'test'):
    config.remove_option('splitter', 'test')
    write_config()


# --stop_after splitter
config.read('pygmap3.cfg')
if args.stop_after == "splitter":
    print()
    info(region + ".o5m successful splitted")
    print()
    quit()


# render the map-images
mkgmap.render()


#  remove test option
if config.has_option('mkgmap', 'test'):
    config.remove_option('mkgmap', 'test')
    write_config()


for i in ['splitter', 'mkgmap']:
    if config.has_option(i, 'old_version'):
        config.remove_option(i, 'old_version')
    write_config()


# --stop_after mkgmap
if args.stop_after == "mkgmap":
    config.read('pygmap3.cfg')
    print()
    info("Mapset for " + region + " successful created")
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


#if os.path.isfile("pygmap3.lck"):
#    os.remove("pygmap3.lck")


print()
print()
print(" ----- " + DATE + " ----- " + region + " ready! -----")
print()
print()


quit()
