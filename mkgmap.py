#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import shutil


WORK_DIR = os.environ['HOME'] + "/map_build/"


def info(msg):
    print("II: " + msg)


def warning(msg):
    print("WW: " + msg)


def error(msg):
    print("EE: " + msg)


config = configparser.ConfigParser()


def typ_txt_test():
    os.chdir(WORK_DIR)
    global typ_file
    global style_file
    typ_file = WORK_DIR + "styles/styles_typ.typ"
    txt_file = WORK_DIR + "styles/styles_typ.txt"

    if (layer == "defaultmap"):
        typ_file = " "
        style_file = ("--style-file=" + WORK_DIR +
                      config['mkgmap']['rev'] +
                      "/examples/styles/default/ ")
    else:
        if os.path.exists(typ_file) and os.path.exists(txt_file):
            m1 = os.path.getmtime(typ_file)
            m2 = os.path.getmtime(txt_file)
            if m1 > m2:
                typ_file = typ_file
            elif m2 > m1:
                typ_file = txt_file
                print()
                warning("styles_typ.typ and styles_typ.txt exist, " +
                        " use the newer file")
                print()
                info("typ_file   = " + typ_file)
                print()
        elif os.path.exists(WORK_DIR + "styles/" + layer + "_typ.typ"):
            typ_file = WORK_DIR + "styles/" + layer + "_typ.typ"
        elif os.path.exists(WORK_DIR + "styles/" + layer + "_typ.txt"):
            typ_file = WORK_DIR + "styles/" + layer + "_typ.txt"
        elif os.path.exists(typ_file):
            typ_file = typ_file
        elif os.path.exists(txt_file):
            typ_file = txt_file
        else:
            print()
            warning(layer + " build without a typ_file")
            typ_file = " "
        style_file = (" --style-file=" + WORK_DIR +
                      "styles/" + layer + "_style ")


# style check
def check():
    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    mkgmap = config['mkgmap']['rev'] + "/mkgmap.jar "

    global layer
    for layer in config['map_styles']:
        if config['map_styles'][layer] == "yes":
            print()
            print()
            info("checking needed files to build " + layer)
            typ_txt_test()
            print()
            info("typ_file   = " + WORK_DIR + typ_file)
            print()
            info("style_file = " + WORK_DIR + style_file)
            print()

            defaultmap_opts = (" --split-name-index " +
                               " --route " +
                               " --housenumbers " +
                               " --index ")
            style_opts = WORK_DIR + "styles/" + (layer) + "_style/options "
            base_opts = WORK_DIR + "styles/options "

            if layer == "defaultmap":
                options = defaultmap_opts
            elif os.path.exists(style_opts):
                options = style_opts
            else:
                options = base_opts

            os.system("java -jar " +
                      WORK_DIR + mkgmap +
                      " -c " + options +
                      " --style-file=" +
                      style_file +
                      " --check-styles " +
                      typ_file)
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
    buildmap = config['runtime']['buildmap']

    global layer
    for layer in config['map_styles']:

        if config['map_styles'][layer] == "yes":

            # Test for (layer)-dir and remove old data from there

            if not os.path.exists(layer):
                os.mkdir(layer)
            else:
                path = layer
                for file in os.listdir(path):
                    if os.path.isfile(os.path.join(path, file)):
                        os.remove(os.path.join(path, file))

            # Java HEAP, RAM oder Mode

            if config['java']['agh'] == "1":
                heap = " -XX:+AggressiveHeap "
            else:
                heap = (config['java']['xmx'] + config['java']['xms'])

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
                logging = (" -Dlog.config=log.props ")

            # options to create hillshading
            dem = " "
            dem_dists = " "
            poly = " "
            conf_1 = config['demtdb']['switch_tdb']
            conf_2 = config['tdblayer'][layer]

            if conf_1 == "yes" and conf_2 == "yes":
                dem_dists = (" --dem-dists=" + config['demtdb']['demdists'])
                poly = (" --dem-poly=" +
                        WORK_DIR + "poly/" + buildmap + ".poly ")

                dem = " --dem="
                demdir = WORK_DIR + "hgt/COPERNICUS"
                if os.path.exists(demdir):
                    dem = dem + demdir
                hgtdir1 = WORK_DIR + "hgt/VIEW1"
                if os.path.exists(hgtdir1):
                    dem = dem + "," + hgtdir1
                hgtdir3 = WORK_DIR + "hgt/VIEW3"
                if os.path.exists(hgtdir3):
                    dem = dem + "," + hgtdir3

                if dem == " --dem=":
                    dem = " "
                    dem_dists = " "
                    poly = " "
                    warning(" building a map without hillshading ")
                    print()

            # create a windows installer
            if config.has_option('runtime', 'installer'):
                installer = " --nsis --tdbfile "
            else:
                installer = " "

            # set the name tag list
            if layer == "fixme" or layer == "boundary":
                name_tag_list = " "
            elif config.has_option('name_tag_list', buildmap):
                name_tag_list = (" --name-tag-list=" +
                                 config['name_tag_list'][buildmap])
            else:
                name_tag_list = (" --name-tag-list=" +
                                 config['name_tag_list']['default'])

            # settings for precomp bounds and sea
            if layer == "fixme" or layer == "boundary":
                bounds = " "
            else:
                bounds = " --location-autofill=is_in,nearest "
                if config.has_option('precomp', 'bounds'):
                    bounds_zip = (WORK_DIR + "precomp/" +
                                  config['precomp']['bounds'])
                    if os.path.exists(bounds_zip):
                        bounds = " --bounds=" + bounds_zip

            if layer == "fixme" or layer == "boundary":
                sea = " "
            else:
                sea = (" --generate-sea=extend-sea-sectors," +
                       "close-gaps=6000,floodblocker," +
                       "land-tag=natural=background ")
                if config.has_option('precomp', 'sea'):
                    sea_zip = WORK_DIR + "precomp/" + config['precomp']['sea']
                    if os.path.exists(sea_zip):
                        sea = (" --precomp-sea=" +
                               sea_zip + " --generate-sea ")

            # style options
            defaultmap_opts = (" --split-name-index " +
                               " --route " +
                               " --housenumbers " +
                               " --index ")
            style_opts = WORK_DIR + "styles/" + layer + "_style/options"
            base_opts = WORK_DIR + "styles/options "

            if layer == "defaultmap":
                options = defaultmap_opts
            elif os.path.exists(style_opts):
                options = " -c " + style_opts
            else:
                options = " -c " + base_opts

            if config.has_option('runtime', 'use_spec_opts'):
                spec_opts = (" --report-similar-arcs --report-dead-ends ")
            else:
                spec_opts = " "

            # street name index options
            index = (WORK_DIR + config['mkgmap']['rev'] +
                     "/examples/roadNameConfig.txt")
            if layer == "fixme" or layer == "boundary":
                index_opts = " "
            elif os.path.exists(index):
                index_opts = (" --road-name-config=" + index)
            else:
                index_opts = " "

            # use  TYP or TXT
            typ_txt_test()

            os.chdir(layer)
            print()
            info("building " + layer)
            print()

            # map rendering
            command_line = ("java -ea " +
                            heap +
                            logging +
                            " -jar " + WORK_DIR + mkgmap +
                            keep_going +
                            max_jobs +
                            bounds +
                            sea +
                            style_file +
                            name_tag_list +
                            " --levels=" + config['maplevel']['levels'] +
                            dem +
                            dem_dists +
                            poly +
                            " --mapname=" + config['mapid'][buildmap] +
                            config[layer]['mapid_ext'] +
                            " --family-id=" + config['mapid'][buildmap] +
                            " --product-id=" + config[layer]['product-id'] +
                            " --family-name=" + buildmap + "_" + layer +
                            " --series-name=" + buildmap + "_" + layer +
                            " --draw-priority=" +
                            config[layer]['draw-priority'] +
                            " --description=" + buildmap + "_" + layer +
                            options +
                            spec_opts +
                            index_opts +
                            installer +
                            " --gmapsupp " +
                            WORK_DIR + "tiles/*.o5m " +
                            typ_file)

            if config.has_option('runtime', 'verbose'):
                print()
                info(command_line)
                print()

            os.system(command_line)

            os.chdir(WORK_DIR)

            # move gmapsupp.img to unzip_dir as buildmap_(layer)_gmapsupp.img

            unzip_dir = "gps_ready/unzipped/" + buildmap

            bl = buildmap + "_" + layer
            img = unzip_dir + "/" + bl + "_gmapsupp.img"

            if not os.path.exists(unzip_dir):
                os.makedirs(unzip_dir)

            if os.path.exists(img):
                os.remove(img)

            shutil.move(layer + "/gmapsupp.img", img)
