#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import http.client
import re
import tarfile
import configparser
import urllib.request
import shutil


WORK_DIR = os.environ['HOME'] + "/map_build/"


def printinfo(msg):
    print("II: " + msg)


def printwarning(msg):
    print("WW: " + msg)


def printerror(msg):
    print("EE: " + msg)


config = configparser.ConfigParser()

"""
config writer
"""


def write_config():
    with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)


"""
get splitter and mkgmap

"""


def from_mkgmap_org():
    config.read('pygmap3.cfg')

    for i in ['splitter', 'mkgmap']:
        target = http.client.HTTPConnection("www.mkgmap.org.uk")
        target.request("GET", "/download/" + i + ".html")
        htmlcontent = target.getresponse()
        data = htmlcontent.read()
        data = data.decode('utf8')

        if config.has_option('runtime', 'use_mkgmap_test') and i == "mkgmap":
            mkgmap_test = config['runtime']['mkgmap_test']

            pattern = re.compile("mkgmap-" + mkgmap_test + "-r\d{4}.zip")
            i_rev_pre = sorted(pattern.findall(data), reverse=True)[0]
            i_rev = os.path.splitext(os.path.basename(i_rev_pre))[0]

        else:
            if i == "splitter":
                pattern = re.compile('splitter-r\d{3}.zip')
            elif i == "mkgmap":
                pattern = re.compile('mkgmap-r\d{4}.zip')

            i_rev_pre = sorted(pattern.findall(data), reverse=True)[0]
            i_rev = os.path.splitext(os.path.basename(i_rev_pre))[0]

            target.close()

        if not os.path.exists(i_rev):
            if os.path.isfile(i_rev + ".tar.gz"):
                tar = tarfile.open((i_rev) + ".tar.gz")
                tar.extractall()
                tar.close()
            else:
                url = "http://www.mkgmap.org.uk/download/" + i_rev + ".tar.gz"
                file = i_rev + ".tar.gz"
                print()
                printinfo("download " + url)

                # Download the file from `url` and save it under `file_name`:
                urlopen = urllib.request.urlopen
                with urlopen(url) as response, open(file, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)

                tar = tarfile.open((i_rev) + ".tar.gz")
                tar.extractall()
                tar.close()

        if config.has_option('runtime', 'use_mkgmap_test') and i == "mkgmap":
            print()
            printinfo("using " + i_rev)

        config.set('runtime', i, i_rev)
        write_config()
