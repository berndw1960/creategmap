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


def create_o5m():

    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    buildmap = config['runtime']['buildmap']

    if os.path.exists("o5m/" + buildmap + "osm.pbf"):
        print()
        info("converting o5m/" + buildmap +
             ".osm.pbf to o5m/" + buildmap +
             ".o5m, please wait...")
        os.system("osmconvert o5m/" + buildmap +
                  ".osm.pbf -o=o5m/" + buildmap +
                  ".o5m")

    elif os.path.exists("o5m/" + buildmap + "-latest.osm.pbf"):
        print()
        info("converting o5m/" + buildmap +
             "-latest.osm.pbf to o5m/" + buildmap +
             ".o5m, please wait...")
        os.system("osmconvert o5m/" + buildmap +
                  "-latest.osm.pbf -o=o5m/" + buildmap + ".o5m")

    elif os.path.exists("planet/planet.o5m"):
        ftime = os.path.getmtime("planet/planet.o5m")
        curtime = time.time()
        difftime = curtime - ftime
        if difftime > 1741800:
            print()
            warn("Your planet file is older then one month")
            print(" You should update it.")
        if os.path.exists("poly/" + buildmap + ".poly"):
            print()
            info("now extracting " + buildmap +
                 ".o5m from Planet, please wait...")
            os.system("osmconvert planet/planet.o5m " +
                      "--complete-ways --complex-ways --drop-version " +
                      " -B=poly/" + buildmap + ".poly " +
                      " -o=o5m/" + buildmap + ".o5m")
        else:
            print()
            error("missing poly/" + buildmap + ".poly")
            print()
            info("created it or try to get one from" +
                 " http://download.geofabrik.de ")
            print("    or use another source for this file")
            print()
            quit()

    else:
        print()
        error((WORK_DIR) + "o5m/" + buildmap + ".o5m not found! ")
        print()
        quit()


def update_o5m():

    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    buildmap = config['runtime']['buildmap']

    if config.has_option('runtime', 'minutely'):
        update_opts = " --hourly -- minutely "
    elif config.has_option('runtime', 'hourly'):
        update_opts = " --hourly "
    else:
        update_opts = " "

    print()
    info("updating " + buildmap + ".o5m, please wait...")
    poly = " "
    if os.path.exists("poly/" + buildmap + ".poly"):
        poly = " -B=poly/" + buildmap + ".poly "
    os.system("osmupdate --daily" +
              update_opts +
              poly +
              " --keep-tempfiles o5m/" +
              buildmap +
              ".o5m  o5m/" + buildmap + "_new.o5m")

    os.chdir("o5m")

    if os.path.exists(buildmap + "_new.o5m"):
        os.rename(buildmap + ".o5m", buildmap + "_temp.o5m")
        os.rename(buildmap + "_new.o5m", buildmap + ".o5m")
        if os.path.exists(buildmap + ".o5m"):
            os.remove(buildmap + "_temp.o5m")

    os.chdir(WORK_DIR)

    write_config()
