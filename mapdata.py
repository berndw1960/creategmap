#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import datetime
import configparser


WORK_DIR = (os.environ['HOME'] + "/map_build/")


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


"""
cut data from planet-file

"""


def create_o5m():

    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    buildmap = config['runtime']['buildmap']

    if os.path.exists("o5m/" + buildmap + "osm.pbf"):
        print()
        printinfo("""converting o5m/""" + buildmap +
                  """.osm.pbf to o5m/""" + buildmap +
                  """.o5m, please wait...""")
        os.system("""osmconvert o5m/""" + buildmap +
                  """.osm.pbf -o=o5m/""" + buildmap +
                  """.o5m""")

    elif os.path.exists("o5m/" + buildmap + "-latest.osm.pbf"):
        print()
        printinfo("""converting o5m/""" + buildmap +
                  """-latest.osm.pbf to o5m/""" + buildmap +
                  """.o5m, please wait...""")
        os.system("""osmconvert o5m/""" + buildmap +
                  """-latest.osm.pbf -o=o5m/""" + buildmap + """.o5m""")

    elif os.path.exists("planet/planet.o5m"):
        if os.path.exists("poly/" + buildmap + ".poly"):
            print()
            printinfo("""now extracting """ + buildmap +
                      """.o5m from Planet, please wait...""")
            os.system("osmconvert planet/planet.o5m " +
                      "--complete-ways --complex-ways --drop-version " +
                      " -B=poly/" + buildmap + ".poly " +
                      " -o=o5m/" + buildmap + ".o5m")
        else:
            print()
            printerror("missing poly/" + buildmap + ".poly")
            print()
            printinfo("""created it or try to get one from
                http://download.geofabrik.de """)
            print("    or use another source for this file")
            print()
            quit()

    else:
        print()
        printerror((WORK_DIR) + "o5m/" + buildmap + ".o5m not found! ")
        print()
        quit()


def update_o5m():

    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    buildmap = config['runtime']['buildmap']
    time = datetime.datetime.now()

    if config.has_option('runtime', 'minutely'):
        update_opts = " --hourly -- minutely "
        DATE = time.strftime('%Y%m%d_%H%M')
    elif config.has_option('runtime', 'hourly'):
        update_opts = " --hourly "
        DATE = time.strftime('%Y%m%d_%H00')
    else:
        update_opts = " "
        DATE = time.strftime('%Y%m%d_0000')

    print()
    printinfo("updating " + buildmap + ".o5m, please wait...")
    option_poly = " "
    if os.path.exists("poly/" + buildmap + ".poly"):
        option_poly = " -B=poly/" + buildmap + ".poly "
    os.system("osmupdate --daily" +
              update_opts +
              option_poly +
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

    config.set('runtime', buildmap, DATE)

    write_config()
