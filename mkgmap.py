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
    global option_typ_file
    global option_style_file
    typ_file = "styles/styles_typ.typ"
    txt_file = "styles/styles_typ.txt"

    if (layer == "defaultmap"):
        option_typ_file = " "
        option_style_file = ("--style-file=" + WORK_DIR +
                             config['runtime']['mkgmap'] +
                             "/examples/styles/default/ ")
    else:
        if os.path.exists(typ_file) and os.path.exists(txt_file):
            m1 = os.path.getmtime(typ_file)
            m2 = os.path.getmtime(txt_file)
            if m1 > m2:
                option_typ_file = " " + WORK_DIR + typ_file
            elif m2 > m1:
                option_typ_file = " " + WORK_DIR + txt_file
                print()
                warning("styles_typ.typ and styles_typ.txt exist, " +
                        " use the newer file")
                print()
                info("typ_file   = " + option_typ_file)
                print()
        elif os.path.exists("styles/" + layer + "_typ.typ"):
            option_typ_file = " " + WORK_DIR + "styles/" + layer + "_typ.typ"
        elif os.path.exists("styles/" + layer + "_typ.txt"):
            option_typ_file = " " + WORK_DIR + "styles/" + layer + "_typ.txt"
        elif os.path.exists(typ_file):
            option_typ_file = " " + WORK_DIR + typ_file
        elif os.path.exists(txt_file):
            option_typ_file = " " + WORK_DIR + txt_file
        else:
            print()
            warning(layer + " build without a typ_file")
            option_typ_file = " "
        option_style_file = (" --style-file=" +
                             WORK_DIR + "styles/" + layer + "_style ")


# style check


def check():
    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    option_mkgmap_path = (WORK_DIR +
                          config['runtime']['mkgmap'] + "/mkgmap.jar ")

    global layer
    for layer in config['map_styles']:
        if config['map_styles'][layer] == "yes":
            print()
            print()
            info("checking needed files to build " + layer)
            typ_txt_test()
            print()
            info("typ_file   = " + option_typ_file)
            print()
            info("style_file = " + option_style_file)
            print()

            mkgmap_defaultmap_opts = (" --split-name-index " +
                                      " --route " +
                                      " --housenumbers " +
                                      " --index ")
            mkgmap_style_opts = (WORK_DIR + "styles/" +
                                 (layer) + "_style/options")
            mkgmap_base_opts = WORK_DIR + "styles/options "

            if layer == "defaultmap":
                option_mkgmap_options = mkgmap_defaultmap_opts
            elif os.path.exists(mkgmap_style_opts):
                option_mkgmap_options = mkgmap_style_opts
            else:
                option_mkgmap_options = mkgmap_base_opts

            os.system("java -jar " +
                      option_mkgmap_path +
                      " -c " + option_mkgmap_options +
                      " --style-file=" +
                      option_style_file +
                      " --check-styles " +
                      option_typ_file)
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
            os.chdir(WORK_DIR)

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
                option_java_heap = " -XX:+AggressiveHeap "
            else:
                option_java_heap = (" " + config['java']['xmx'] +
                                    " " + config['java']['xms'] + " ")

            # mkgmap-options

            option_mkgmap_path = (WORK_DIR + config['runtime']['mkgmap'] +
                                  "/mkgmap.jar ")
            option_mkgmap_jobs = " "
            if config['runtime']['max_jobs'] != "yes":
                if config['runtime']['max_jobs'] == "no":
                    option_mkgmap_jobs = " --max-jobs=1 "
                else:
                    option_mkgmap_jobs = (" --max-jobs=" +
                                          config['runtime']['max_jobs'])
            else:
                option_mkgmap_jobs = " --max-jobs "

            option_keep_going = " "
            if config.has_option('runtime', 'keep_going'):
                option_keep_going = " --keep-going "

            option_mkgmap_logging = " "
            if config.has_option('runtime', 'logging'):
                option_mkgmap_logging = (" -Dlog.config=" +
                                         WORK_DIR + "mkgmap_log.props ")

            # options to create hillshading

            option_mkgmap_dem = " "
            option_mkgmap_dem_dists = " "
            option_mkgmap_poly = " "
            conf_1 = config['runtime']['tdb']
            conf_2 = config['demtdb']['switch_tdb']
            conf_3 = config['tdblayer'][layer]

            if (conf_1 == "yes" or conf_2 == "yes") and conf_3 == "yes":
                # if conf_3 == "yes":
                option_mkgmap_dem_dists = (" --dem-dists=" +
                                           config['demtdb']['demdists'] +
                                           " ")
                option_mkgmap_poly = (" --dem-poly=" +
                                      WORK_DIR + "poly/" +
                                      buildmap + ".poly ")

                option_mkgmap_dem = " --dem="
                demdir = WORK_DIR + "hgt/COPERNICUS"
                if os.path.exists(demdir):
                    option_mkgmap_dem = option_mkgmap_dem + demdir
                hgtdir1 = WORK_DIR + "hgt/VIEW1"
                if os.path.exists(hgtdir1):
                    option_mkgmap_dem = option_mkgmap_dem + "," + hgtdir1
                hgtdir3 = WORK_DIR + "hgt/VIEW3"
                if os.path.exists(hgtdir3):
                    option_mkgmap_dem = option_mkgmap_dem + "," + hgtdir3

                if option_mkgmap_dem == " --dem=":
                    option_mkgmap_dem = " "
                    option_mkgmap_dem_dists = " "
                    option_mkgmap_poly = " "
                    warning(" building a map without hillshading ")
                    print()

            if config.has_option('runtime', 'installer'):
                option_mkgmap_installer = " --nsis --tdbfile "
            else:
                option_mkgmap_installer = " "

            if layer == "fixme" or layer == "boundary":
                option_name_tag_list = " "
            elif config.has_option('name_tag_list', buildmap):
                option_name_tag_list = (" --name-tag-list=" +
                                        config['name_tag_list'][buildmap])
            else:
                option_name_tag_list = (" --name-tag-list=" +
                                        config['name_tag_list']['default'])

            if layer == "fixme" or layer == "boundary":
                option_bounds = " "
            else:
                option_bounds = " --location-autofill=is_in,nearest "
                if config.has_option('precomp', 'bounds'):
                    bounds_zip = (WORK_DIR + "precomp/" +
                                  config['precomp']['bounds'])
                    if os.path.exists(bounds_zip):
                        option_bounds = " --bounds=" + bounds_zip

            if layer == "fixme" or layer == "boundary":
                option_sea = " "
            else:
                option_sea = (" --generate-sea=extend-sea-sectors," +
                              "close-gaps=6000,floodblocker," +
                              "land-tag=natural=background ")
                if config.has_option('precomp', 'sea'):
                    sea_zip = WORK_DIR + "precomp/" + config['precomp']['sea']
                    if os.path.exists(sea_zip):
                        option_sea = (" --precomp-sea=" +
                                      sea_zip + " --generate-sea ")

            mkgmap_defaultmap_opts = (" --split-name-index " +
                                      " --route " +
                                      " --housenumbers " +
                                      " --index ")
            mkgmap_style_opts = WORK_DIR + "styles/" + layer + "_style/options"
            mkgmap_base_opts = WORK_DIR + "styles/options "

            if layer == "defaultmap":
                option_mkgmap_options = mkgmap_defaultmap_opts
            elif os.path.exists(mkgmap_style_opts):
                option_mkgmap_options = " -c " + mkgmap_style_opts
            else:
                option_mkgmap_options = " -c " + mkgmap_base_opts

            if config.has_option('runtime', 'use_spec_opts'):
                option_mkgmap_spec_opts = (" --report-similar-arcs " +
                                           " --report-dead-ends ")
            else:
                option_mkgmap_spec_opts = " "

            mkgmap_index_file = (WORK_DIR +
                                 config['runtime']['mkgmap'] +
                                 "/examples/roadNameConfig.txt")

            if layer == "fixme" or layer == "boundary":
                option_mkgmap_index_opts = " "
            elif os.path.exists(mkgmap_index_file):
                option_mkgmap_index_opts = (" --road-name-config=" +
                                            mkgmap_index_file)
            else:
                option_mkgmap_index_opts = " "

            typ_txt_test()

            os.chdir(layer)
            print()
            info("building " + layer)
            print()

            # map rendering

            command_line = ("java -ea " +
                            option_java_heap +
                            option_mkgmap_logging +
                            " -jar " + option_mkgmap_path +
                            option_keep_going +
                            option_mkgmap_jobs +
                            option_bounds +
                            option_sea +
                            option_style_file +
                            option_name_tag_list +
                            " --levels=" + config['maplevel']['levels'] +
                            option_mkgmap_dem +
                            option_mkgmap_dem_dists +
                            option_mkgmap_poly +
                            " --mapname=" + config['mapid'][buildmap] +
                            config[layer]['mapid_ext'] +
                            " --family-id=" + config['mapid'][buildmap] +
                            " --product-id=" + config[layer]['product-id'] +
                            " --family-name=" + buildmap + "_" + layer +
                            " --series-name=" + buildmap + "_" + layer +
                            " --draw-priority=" +
                            config[layer]['draw-priority'] +
                            " --description=" + buildmap + "_" + layer +
                            option_mkgmap_options +
                            option_mkgmap_spec_opts +
                            option_mkgmap_index_opts +
                            option_mkgmap_installer +
                            " --gmapsupp " +
                            WORK_DIR + "tiles/*.o5m " +
                            option_typ_file)

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
