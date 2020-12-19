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


# cut data from planet-file
def error_raw_data():
    message = (" \n "
               " Oops, something went wrong while creating the raw data file "
               " \n ")
    print(message)
    quit()


def create_o5m():

    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    region = config['runtime']['region']

    if os.path.exists("pbf/" + region + "osm.pbf"):
        print()
        info("converting pbf/" + region
             + ".osm.pbf to o5m/" + region
             + ".o5m, please wait...")
        os.system("osmconvert pbf/" + region
                  + "--drop-version "
                  + "--drop-author "
                  + ".osm.pbf -o=o5m/" + region
                  + ".o5m")
        if os.path.exists("o5m/" + region + ".o5m"):
            os.remove("pbf/" + region + ".osm.pbf")
        else:
            error_raw_data()

    elif os.path.exists("pbf/" + region + "-latest.osm.pbf"):
        print()
        info("converting pbf/" + region
             + "-latest.osm.pbf to o5m/" + region
             + ".o5m, please wait...")
        os.system("osmconvert pbf/" + region
                  + "--drop-version "
                  + "--drop-author "
                  + "-latest.osm.pbf -o=o5m/" + region + ".o5m")
        if os.path.exists("o5m/" + region + ".o5m"):
            os.remove("pbf/" + region + "-latest.osm.pbf")
        else:
            error_raw_data()

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
                      + " -B=poly/" + region + ".poly "
                      + " -o=o5m/" + region + ".o5m")
        else:
            print()
            error("missing poly/" + region + ".poly")
            print()
            info("created it or try to get one from \n\n"
                 + " http://download.geofabrik.de \n\n "
                 + " or use another source for this file")
            print()
            quit()

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
    os.system("osmupdate --daily"
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
