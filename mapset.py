#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import argparse
import build_config
import time


WORK_DIR = os.environ['HOME'] + "/map_build/"


# set prefix for messages
def info(msg):
    print("II: " + msg)


def warn(msg):
    print("WW: " + msg)


def error(msg):
    print("EE: " + msg)


if not os.path.exists(WORK_DIR):
    error("Please create" + WORK_DIR)
    quit()


os.chdir(WORK_DIR)


if os.path.exists("stop"):
    os.remove("stop")


# configparser
def write_config():
    with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)


config = configparser.ConfigParser()


if not os.path.exists("pygmap3.cfg"):
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


def remove_faststyle():
    if config.has_section('faststyle'):
        for key in (config['faststyle']):
            config.remove_option('faststyle', key)
        config.remove_section('faststyle')
    if config.has_option('runtime', 'faststyle'):
        config.remove_option('runtime', 'faststyle')


remove_faststyle()


write_config()


# argparse
parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\

          This Program create mapsets for different regions for Garmin PNA
        '''))

# mapsets
parser.add_argument('-am', '--add_mapset', default=0, nargs='*',
                    help="add a space separated list of mapsets")
parser.add_argument('-ap', '--add_poly', action="store_true",
                    help="add mapsets by using all poly files in " +
                    WORK_DIR + "poly")
parser.add_argument('-af', '--add_folder', action="store_true",
                    help="add mapsets using the names of the folders in " +
                    WORK_DIR + "gps_ready/zipped")
parser.add_argument('-ao', '--add_o5m', action="store_true",
                    help="add mapsets using the names of the o5m files in " +
                    WORK_DIR + "o5m")
parser.add_argument('-em', '--enable_mapset', default=0, nargs='*',
                    help="enable a space separated list of mapsets," +
                    " ALL for all mapsets on the list")
parser.add_argument('-dm', '--disable_mapset', default=0, nargs='*',
                    help="disable a space separated list of mapsets, " +
                    " ALL for all mapsets on the list")
parser.add_argument('-rm', '--remove_mapset', default=0, nargs='*',
                    help="delete a space separated list of mapsets," +
                    " ALL for all mapsets on the list")
parser.add_argument('-lm', '--list_mapset', action="store_true",
                    help="print out the mapset list")
parser.add_argument('-fb', '--fastbuild', default=0, nargs='*',
                    help="a space separated list of mapsets")
parser.add_argument('-fs', '--faststyle', default=0, nargs='*',
                    help="a space separated list of styles for the default " +
                    "region, to set the region, us 'pygmap3.py -s $REGION' ")
parser.add_argument('-ba', '--break_after', default=0,
                    help="break mapset creating after this" +
                    " changeset, use '-lm' for the list")

# pygmap3
parser.add_argument('-nz', '--no_zip', action="store_true",
                    help="don't zip the images after build")
parser.add_argument('-c', '--contourlines', action="store_true",
                    help="enable countourlines layer creation")
parser.add_argument('-st', '--stop_after', default=0,
                    help="build process stop after" +
                    " [tests|contourlines|mapdata|splitter|mkgmap]")
parser.add_argument('-l', '--log', action="store_true",
                    help="enable splitter and mkgmap logging")
parser.add_argument('-v', '--verbose', action="store_true",
                    help="increase verbosity")
parser.add_argument('-mt', '--test', action="store_true",
                    help="use a svn version of mkgmap like housenumbers2")
parser.add_argument('-so', '--spec_opts', action="store_true",
                    help="use some special opts to test the raw data")

args = parser.parse_args()


def mapset_backup():
    if not config.has_section('mapset_backup'):
        config.add_section('mapset_backup')
    for key in (config['mapset']):
        config.set('mapset_backup', key, config['mapset'][key])
        config.set('mapset', key, 'no')


if args.faststyle:
    if not args.fastbuild:
        mapset_backup()
        config.set('mapset', config['runtime']['default_region'], 'yes')
    if not config.has_section('faststyle'):
        config.add_section('faststyle')
    for style in args.faststyle:
        if not config.has_section('mapstyles'):
            config.add_section('mapstyles')
        if os.path.exists("styles/" + style + "_style"):
            config.set('mapstyles', style, 'yes')
            config.set('faststyle', style, 'yes')
        else:
            print()
            warn("Style " + style + " not found")
            print()
    config.set('runtime', 'faststyle', '1')


if args.fastbuild:
    mapset_backup()
    for region in args.fastbuild:
        if os.path.exists("poly/" + region + ".poly" or
                          "o5m/" + region + ".o5m"):
            config.set('mapset', region, 'yes')
        else:
            print()
            warn("Neither " + region + ".poly nor " + region + ".o5m found!")
            print()


# set, edit or delete mapset list
if args.add_poly:
    path = WORK_DIR + "poly"
    dir = sorted(os.listdir(path))
    for file in dir:
        file = os.path.splitext(file)[0]
        if config.has_option('mapset', file):
            continue
        else:
            config.set('mapset', file, 'no')
    write_config()
    print()
    warn("ALL poly files added to mapset list, but not enabled!")
    print()
    info("To enable a mapset, use '--enable_mapset ALL' for whole list")
    info("or '--enable_mapset $POLY' for a special mapset")
    print()
    quit()


if args.add_folder:
    mapset_backup()
    path = WORK_DIR + "gps_ready/zipped"
    dir = sorted(os.listdir(path))
    for folder in dir:
        if not config.has_option('mapset', folder):
            config.set('mapset', folder, 'yes')
    for key in (config['mapset']):
        config.set('mapset', key, 'yes')


if args.add_o5m:
    mapset_backup()
    for region in os.listdir("o5m"):
        file = os.path.splitext(os.path.basename(region))[0]
        if not config.has_option('mapset', file):
            config.set('mapset', file, 'yes')
        for key in (config['mapset']):
            config.set('mapset', key, 'yes')


if args.add_mapset:
    for region in args.add_mapset:
        file = os.path.splitext(os.path.basename(region))[0]
        if not config.has_option('mapset', region):
            if not os.path.exists("poly/" + region + ".poly"):
                print()
                error(WORK_DIR + "poly/" + file + ".poly not found... ")
                print("please create or download " + file + ".poly")
                print()
                quit()
        config.set('mapset', region, 'yes')
        if not config.has_section(region):
            config.add_section(region)
            config.set(region, 'new_region', 'yes')
    write_config()
    print()
    info(" please check the options for this mapset with:   pygmap3.py -e")
    print()
    quit()


if args.enable_mapset == "ALL":
    mapset_backup()
    for key in (config['mapset']):
        config.set('mapset', key, 'yes')
elif args.enable_mapset:
    for region in args.enable_mapset:
        config.set('mapset', region, 'yes')
    write_config()
    quit()


if args.disable_mapset == "ALL":
    for key in (config['mapset']):
        config.set('mapset', key, 'no')
    write_config()
    quit()
elif args.disable_mapset:
    for region in args.disable_mapset:
        config.set('mapset', region, 'no')
    write_config()
    quit()


if args.remove_mapset == "ALL":
    config.remove_section('mapset')
    write_config()
    quit()
elif args.remove_mapset:
    for region in args.remove_mapset:
        config.remove_option('mapset', region)
    write_config()
    quit()


if args.list_mapset:
    if config.has_section('mapset'):
        print()
        info("mapset list includes: ")
        print()
        print("    enabled:")
        for key in (config['mapset']):
            if config['mapset'][key] == "yes":
                print("      " + key)
        print()
        print("    disabled:")
        for key in config['mapset']:
            if config['mapset'][key] == "no":
                print("      " + key)
    else:
        print()
        info("mapset list didn't exist")
    print()
    quit()


write_config()


# build or additional option for pygmap3
if args.stop_after:
    stop = "-st " + args.stop_after + " "
else:
    stop = ""


if args.contourlines:
    cl = "-c "
else:
    cl = ""


if args.test and config.has_option('runtime', 'test'):
    test = "-mt "
else:
    test = ""


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


command_line = ("pygmap3.py -kg " +
                verbose + stop + cl + test + log + zip)


print()
info("Ready to start?   ")
print()
print("    In the next 5 seconds you can stop ")
print("    building the maps with STRG+C ")
counter = 5
while counter > 0:
    counter -= 1
    time.sleep(1)


config.set('runtime', 'mapset', "1")
write_config()


for region in config['mapset']:
    if os.path.exists(WORK_DIR + "stop"):
        print()
        error("Process stopped while there is the stop file!")
        print()
        quit()

    if not os.path.exists(WORK_DIR + "stop"):
        file = open('stop', 'w')
        file.write("\n\n emergency break for mapset.py\n"
                   + " this file should not exist, if the last"
                   + " run was successful")
        file.close()

    if config['mapset'][region] == "yes":

        if region == args.break_after:
            print()
            warn("Stopping creating mapsets after this mapset")

        os.system(command_line + "-r " + region)

    if region == args.break_after:
        quit()


remove_faststyle()


config.set('runtime', 'mapset', "0")
write_config()


print()
print("###### all mapsets successfully build! #######")
print()


quit()
