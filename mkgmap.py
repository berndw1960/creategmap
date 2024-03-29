#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import shutil


WORK_DIR = os.path.expanduser('~') + "/map_build/"


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


def typ_txt_test():
    os.chdir(WORK_DIR)
    global typ_file
    global style_file

    if layer == "defaultmap":
        typ_file = " "
        style_file = (WORK_DIR
                      + config['mkgmap']['rev']
                      + "/examples/styles/default ")
    else:
        if os.path.exists(WORK_DIR + "styles/" + layer + "_typ.typ"):
            typ_file = WORK_DIR + "styles/" + layer + "_typ.typ"
        elif os.path.exists(WORK_DIR + "styles/" + layer + "_typ.txt"):
            typ_file = WORK_DIR + "styles/" + layer + "_typ.txt"
        elif os.path.exists(WORK_DIR + "styles/styles_typ.typ"):
            typ_file = WORK_DIR + "styles/styles_typ.typ"
        elif os.path.exists(WORK_DIR + "styles/styles_typ.txt"):
            typ_file = WORK_DIR + "styles/styles_typ.txt"
        else:
            print()
            warn(layer + " build without a typ_file")
            typ_file = " "

        style_file = (WORK_DIR + "styles/" + layer + "_style ")


# style check
def check():
    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    mkgmap = config['mkgmap']['rev'] + "/mkgmap.jar "

    global layer
    for layer in config['mapstyles']:
        if config['mapstyles'][layer] == "yes":
            print()
            print()
            info("checking needed files to build " + layer)
            typ_txt_test()
            print()
            info("typ_file   = " + typ_file)
            print()
            info("style_file = " + style_file)
            print()

            defaultmap_opts = (" --split-name-index "
                               + " --route "
                               + " --housenumbers "
                               + " --index ")
            style_opts = WORK_DIR + "styles/" + layer + "_style/options "
            base_opts = WORK_DIR + "styles/options "

            if layer == "defaultmap":
                options = defaultmap_opts
            elif os.path.exists(style_opts):
                options = style_opts
            else:
                options = base_opts

            os.system("java -jar "
                      + WORK_DIR + mkgmap
                      + " -c " + options
                      + " --style-file="
                      + style_file
                      + " --check-styles "
                      + typ_file)
    print()

    os.chdir(WORK_DIR)

    for i in ['styles_typ.typ',
              'styles/xstyles_typ.typ',
              'splitter.log',
              'osmmap.tdb',
              'osmmap.img',
              'osmmap_mdr.img',
              'osmmap.mdx',
              'basemap_typ.typ',
              'bikemap_typ.typ',
              'carmap_typ.typ', ]:
        if os.path.exists(i):
            os.remove(i)


# map rendering
def render():
    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    region = config['runtime']['region']

    # Java HEAP, RAM oder Mode
    if config['java']['agh'] == "1":
        heap = " -XX:+AggressiveHeap "
    else:
        heap = (config['java']['xmx'] + ' ' + config['java']['xms'])

    # mkgmap-options

    mkgmap = (config['mkgmap']['rev'] + "/mkgmap.jar ")
    max_jobs = " "
    if config['runtime']['max_jobs'] != "yes":
        if config['runtime']['max_jobs'] == "no":
            max_jobs = " --max-jobs=1 "
        else:
            max_jobs = (" --max-jobs=" + config['runtime']['max_jobs'])
    else:
        max_jobs = " --max-jobs "

    keep_going = " "
    if config.has_option('runtime', 'keep_going'):
        keep_going = " --keep-going "

    logging = " "
    if config.has_option('runtime', 'logging'):
        logging = (" -Dlog.config=" + WORK_DIR + "log.props ")

    global layer
    stylelist = []
    if config.has_option('runtime', 'faststyle'):
        for layer in config['faststyle']:
            stylelist.append(layer)
    else:
        for layer in config['mapstyles']:
            if layer in config[region] and (config[region][layer] == "yes" or
                                            config[region][layer] == "tdb"):
                stylelist.append(layer)

    # build the map layer
    for layer in stylelist:
        # Test for (layer)-dir and remove old data from there

        if not os.path.exists(layer):
            os.mkdir(layer)
        else:
            path = layer
            for file in os.listdir(path):
                if os.path.isfile(os.path.join(path, file)):
                    os.remove(os.path.join(path, file))

        # options to create hillshading
        dem = " "
        dem_dists = " "
        poly = " "
        show_profiles = " "

        if layer in config['tdb_layer'] and config[region][layer] == "tdb":
            dem_temp = " "

            demdir = WORK_DIR + "hgt/COPERNICUS"
            if os.path.exists(demdir):
                dem_temp = demdir + ","
                hs = "1"

            hgtdir1 = WORK_DIR + "hgt/VIEW1"
            if os.path.exists(hgtdir1):
                dem_temp = dem_temp + hgtdir1 + ","
                hs = "1"

            hgtdir3 = WORK_DIR + "hgt/VIEW3"
            if os.path.exists(hgtdir3):
                dem_temp = dem_temp + hgtdir3
                hs = "1"

            if hs == "1":
                dem = " --dem=" + dem_temp
                dem_dists = (" --dem-dists=" + config['demtdb']['demdists'])
                show_profiles = " --show-profiles=1 "

                poly_file = WORK_DIR + "poly/" + region + ".poly"
                if os.path.exists(poly_file):
                    poly = (" --dem-poly=" + poly_file)
            else:
                print()
                warn("Couldn't enable hillshading for this layer")

        # set the name tag list
        name_tag_list = ""
        if layer in config['routing_layer']:
            if config.has_option(region, 'name_tag_list'):
                name_tag_list = (" --name-tag-list="
                                 + config[region]['name_tag_list'])
            else:
                name_tag_list = (" --name-tag-list="
                                 + config['name_tag_list']['default'])

        # settings for precomp bounds and sea
        if layer in config['routing_layer']:
            if config.has_option('runtime', 'no_bounds'):
                bounds = " --location-autofill=is_in,nearest "
            elif config.has_option('precomp', 'bounds'):
                bounds_zip = (WORK_DIR + "precomp/"
                              + config['precomp']['bounds'])
                if os.path.exists(bounds_zip):
                    bounds = " --bounds=" + bounds_zip
        else:
            bounds = " "

        if layer in config['routing_layer']:
            sea = (" --generate-sea=extend-sea-sectors,"
                   + "close-gaps=6000,floodblocker,"
                   + "land-tag=natural=background ")

            if config.has_option('runtime', 'no_sea'):
                pass
            elif config.has_option('precomp', 'sea'):
                sea_zip = WORK_DIR + "precomp/" + config['precomp']['sea']
                if os.path.exists(sea_zip):
                    sea = (" --precomp-sea="
                           + sea_zip + " --generate-sea ")
        else:
            sea = " "

#        # exclude routing island
#        # add '+ routing_islands' to the mkgmap options!
#        if layer in config['routing_layer']:
#            routing_islands = " --check-routing-island-len=500 "
#        else:
#            routing_islands = " "

        # style options for routing layer
        if layer in config['routing_layer']:
            defaultmap_opts = (" --split-name-index "
                               + " --route "
                               + " --housenumbers "
                               + " --index ")
        else:
            defaultmap_opts = " "

        style_opts = WORK_DIR + "styles/" + layer + "_style/options"
        base_opts = WORK_DIR + "styles/options "

        if layer == "defaultmap":
            options = defaultmap_opts
        elif os.path.exists(style_opts):
            options = " -c " + style_opts
        else:
            options = " -c " + base_opts

        # following opts are mostly diagnostics output
        if config.has_option('runtime', 'use_spec_opts'):
            spec_opts = (" --report-similar-arcs "
                         + " --report-dead-ends "
                         + " --check-roundabouts "
                         + " --check-roundabout-flares ")
        else:
            spec_opts = " "

        # street name index options
        index = (WORK_DIR + config['mkgmap']['rev'] +
                 "/examples/roadNameConfig.txt")
        if layer in config['routing_layer']:
            index_opts = (" --road-name-config=" + index)
        else:
            index_opts = " "

        # create a windows installer
        if config.has_option('runtime', 'installer'):
            installer = " --nsis --tdbfile "
        else:
            installer = " "

        # use  TYP or TXT
        typ_txt_test()

        os.chdir(layer)
        print()
        info("building " + layer)
        print()

        # map rendering
        command_line = ("java -ea "
                        + heap
                        + logging
                        + " -jar " + WORK_DIR + mkgmap
                        + keep_going
                        + max_jobs
                        + bounds
                        + sea
                        + " --style-file=" + style_file
                        + name_tag_list
                        + " --levels=" + config['maplevel']['levels']
                        + dem
                        + dem_dists
                        + show_profiles
                        + poly
                        + " --mapname=" + config[region]['mapid']
                        + config[layer]['mapid_ext']
                        + " --family-id=" + config[region]['mapid']
                        + " --product-id=" + config[layer]['product-id']
                        + " --family-name=" + region + "_" + layer
                        + " --series-name=" + region + "_" + layer
                        + " --draw-priority="
                        + config[layer]['draw-priority']
                        + " --description=" + region + "_" + layer
                        + options
                        + spec_opts
                        + index_opts
                        + installer
                        + " --gmapsupp "
                        + WORK_DIR + "tiles/*.o5m "
                        + typ_file)

        if config.has_option('runtime', 'verbose'):
            info(command_line)
            print()

        os.system(command_line)

        os.chdir(WORK_DIR)

        # move gmapsupp.img to unzip_dir as region_(layer)_gmapsupp.img
        unzip_dir = "gps_ready/unzipped/" + region
        bl = region + "_" + layer
        img = unzip_dir + "/" + bl + "_gmapsupp.img"

        if not os.path.exists(unzip_dir):
            os.makedirs(unzip_dir)

        if os.path.exists(img):
            os.remove(img)

        shutil.move(layer + "/gmapsupp.img", img)
