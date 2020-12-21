#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import configparser
import time


WORK_DIR = (os.environ['HOME'] + "/map_build/")


def info(msg):
    print("II: " + msg)


def warn(msg):
    print("WW: " + msg)


def error(msg):
    print("EE: " + msg)


# configparser


def write_config():
    with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)


config = configparser.ConfigParser()


def create_o5m():

    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    region = config['runtime']['region']

    if os.path.exists("planet/planet-latest.osm.pbf"):
        os.remane("planet-latest.osm.pbf", "planet.osm.pbf")

    if not os.path.exists("poly/" + region + ".poly"):
        print()
        error("No poly file for " + region + " found!")
        print()
        quit()

    # extracting from planet.o5m --> region.o5m with poly
    if os.path.exists("planet/planet.o5m"):
        ftime = os.path.getmtime("planet/planet.o5m")
        curtime = time.time()
        difftime = curtime - ftime

        if difftime > 1741800:
            print()
            warn("Your planet file is older then one month")
            print("    You should update it.")

        if os.path.exists("poly/" + region + ".poly"):
            print()
            info("now extracting " + region
                 + ".o5m from Planet, please wait...")
            os.system("osmconvert planet/planet.o5m "
                      + "--complete-ways "
                      + "--complete-multipolygons "
                      + "--complete-boundaries "
                      + "--drop-version "
                      + "--drop-author "
                      + "-B=poly/" + region + ".poly "
                      + " -o=o5m/" + region + ".o5m ")

    # extracting from planet.osm.pbf--> region.o5m with poly
    elif os.path.exists("planet/planet.osm.pbf"):
        ftime = os.path.getmtime("planet/planet.osm.pbf")
        curtime = time.time()
        difftime = curtime - ftime

        if difftime > 1741800:
            print()
            warn("Your planet file is older then one month")
            print("    You should update it.")

        if os.path.exists("poly/" + region + ".poly"):
            print()
            info("now extracting " + region
                 + ".o5m from Planet, please wait...")
            os.system("osmconvert planet/planet.osm.pbf "
                      + "--complete-ways "
                      + "--complete-multipolygons "
                      + "--complete-boundaries "
                      + "--drop-version "
                      + "--drop-author "
                      + "-B=poly/" + region + ".poly "
                      + " -o=o5m/" + region + ".o5m ")

    else:
        print()
        error((WORK_DIR) + "o5m/" + region + ".o5m not found! ")
        print()
        quit()


def update_o5m():

    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    region = config['runtime']['region']

    if config.has_option('runtime', 'minutely'):
        update_opts = " --hourly -- minutely "
    elif config.has_option('runtime', 'hourly'):
        update_opts = " --hourly "
    else:
        update_opts = " "

    print()
    info("updating " + region + ".o5m, please wait...")
    poly = " "
    if os.path.exists("poly/" + region + ".poly"):
        poly = " -B=poly/" + region + ".poly "
    os.system("osmupdate --daily "
              + "--drop-version "
              + "--drop-author "
              + update_opts
              + poly
              + " --keep-tempfiles o5m/"
              + region +
              ".o5m  o5m/" + region + "_new.o5m")

    os.chdir("o5m")

    if os.path.exists(region + "_new.o5m"):
        os.rename(region + ".o5m", region + "_temp.o5m")
        os.rename(region + "_new.o5m", region + ".o5m")
        if os.path.exists(region + ".o5m"):
            os.remove(region + "_temp.o5m")

    os.chdir(WORK_DIR)

    write_config()
