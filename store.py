#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import shutil
import zipfile


WORK_DIR = os.environ['HOME'] + "/map_build/"


config = configparser.ConfigParser()


def zip_img():
    # zip the images and move them to separate dirs
    print("\n\n Please wait, zipping the images...\n")
    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')
    region = config['runtime']['region']
    unzip_dir = WORK_DIR + "gps_ready/unzipped/" + region
    zip_dir = WORK_DIR + "gps_ready/zipped/" + region

    if not os.path.exists(zip_dir):
        os.makedirs(zip_dir)

    os.chdir(unzip_dir)
    dir = os.listdir()
    for img in dir:
        zip_img = img + ".zip"
        my_zip_img = zipfile.ZipFile(zip_img, 'w', allowZip64=True)
        my_zip_img.write(img, compress_type=zipfile.ZIP_DEFLATED)
        my_zip_img.close()

        if os.path.exists(zip_dir + "/" + zip_img):
            os.remove(zip_dir + "/" + zip_img)

        shutil.move(zip_img, zip_dir)
        os.remove(unzip_dir + "/" + img)

    os.chdir(WORK_DIR)
    if os.path.exists(unzip_dir):
        shutil.rmtree(unzip_dir)


def kml():
    os.chdir(WORK_DIR)
    region = config['runtime']['region']
    kml_dir = "gps_ready/zipped/" + region

    if not os.path.exists(kml_dir):
        os.makedirs(kml_dir)

    if os.path.exists("tiles/" + region + ".kml"):
        kml = kml_dir + "/" + region + ".kml"
        if os.path.exists(kml):
            os.remove(kml)

        shutil.move("tiles/" + region + ".kml", kml_dir)


def log():
    # save the mkgmap-log for errors
    os.chdir(WORK_DIR)
    config.read('pygmap3.cfg')

    for layer in config['mapstyles']:
        if config['mapstyles'][layer] == "yes":
            region = config['runtime']['region']
            log_dir = ("log/mkgmap/" + region + "/" + layer)

            if os.path.exists(log_dir):
                shutil.rmtree(log_dir)

            if os.path.exists(layer + "/mkgmap.log.0"):
                from shutil import copytree, ignore_patterns
                copytree(layer, log_dir, ignore=ignore_patterns('*.img',
                                                                '*.typ',
                                                                'osm*'))
