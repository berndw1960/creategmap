#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import shutil
import time


WORK_DIR = os.environ['HOME'] + "/map_build/"


def info(msg):
    print("II: " + msg)


def warning(msg):
    print("WW: " + msg)


def write_config():
    with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)


config = configparser.ConfigParser()


# split raw-data
def split():
    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    buildmap = config['runtime']['buildmap']
    splitter = config['splitter']['rev'] + "/splitter.jar "

    # Java HEAP, RAM oder Mode
    if config['java']['agh'] == "1":
        heap = " -XX:+AggressiveHeap "
    else:
        heap = (config['java']['xmx'] + config['java']['xms'])

    java_opts = "java -ea " + heap + " -jar " + WORK_DIR + splitter
    log_opts = " > splitter.log "

    # splitter-options
    BUILD_O5M = WORK_DIR + "o5m/" + buildmap + ".o5m"

    sea = " "
    if config.has_option('precomp', 'sea'):
        sea_zip = WORK_DIR + "precomp/" + config['precomp']['sea']
        if os.path.exists(sea_zip):
            sea = " --precomp-sea=" + sea_zip

    cities15000 = WORK_DIR + "cities15000.zip"
    if os.path.exists(cities15000):
        geonames = " --geonames-file=" + cities15000
    else:
        geonames = " "

    splitter_opts = (geonames +
                     " --mapid=" + config['mapid'][buildmap] + "0001 " +
                     " --output=o5m " +
                     sea +
                     " --write-kml=" + buildmap + ".kml " +
                     " --keep-complete " +
                     " --overlap=0 ")

    areas_list = "areas/" + buildmap + "_areas.list "

    if os.path.exists(areas_list):
        ftime = os.path.getmtime(areas_list)
        curtime = time.time()
        difftime = curtime - ftime
        if difftime > 1741800:
            print()
            warning(buildmap + "_areas.list is older then 1 month, " +
                    "create a new file")
            os.remove(areas_list)

    # split with
    areas = " --split-file=" + areas_list
    # or
    max_nodes = (" --max-nodes=" + config['maxnodes'][buildmap] + " ")

    # splitter.jar command_line
    split_with_areas_list = (java_opts +
                             log_opts +
                             splitter_opts +
                             areas +
                             BUILD_O5M)

    split_without_areas_list = (java_opts +
                                log_opts +
                                splitter_opts +
                                max_nodes +
                                BUILD_O5M)

    if os.path.exists(areas_list):
        command_line = split_with_areas_list
    else:
        command_line = split_without_areas_list

    if config.has_option('runtime', 'verbose'):
        print()
        info(command_line)
        print()

    os.chdir("tiles")
    os.system(command_line)

    if config.has_option('runtime', 'logging'):
        log_dir = WORK_DIR + "log/splitter/" + buildmap

        if os.path.exists(log_dir):
            path = log_dir
            for file in os.listdir(path):
                if os.path.isfile(os.path.join(path, file)):
                    os.remove(os.path.join(path, file))
        else:
            os.makedirs(log_dir)

        for i in ['densities-out.txt',
                  'template.args',
                  'areas.poly',
                  'splitter.log',
                  'areas.list']:
            if os.path.exists(i):
                shutil.copy2(i, log_dir)

    if os.path.exists(areas_list):
        shutil.copy2("areas.list", areas_list)
    file = open(buildmap + "_split.ready", "w")
    file.close()
