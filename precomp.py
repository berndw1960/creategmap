#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import http.client
import re
import urllib.request
import shutil


def info(msg):
    print("II: " + msg)


WORK_DIR = os.environ['HOME'] + "/map_build/"
config = configparser.ConfigParser()


def write_config():
    with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)


def list_bounds():

    config.read('pygmap3.cfg')

    print()
    info("set as used files:")
    print()
    for key in (config['precomp']):
        print("  " + config['precomp'][key])
    print()

    os.chdir(WORK_DIR + "precomp")

    info("local files:")
    for i in ['sea', 'bounds']:
        print()
        dir = os.listdir()
        list = [x for x in dir if x.startswith(i) if x.endswith(".zip")]
        list = sorted(list, reverse=True)
        for i in list:
            print("  " + i)
    print()

    www = "osm.thkukuk.de"
    path = "/data/"

    info("files on thkukuk.de (*-latest not listed):")
    for i in ['sea', 'bounds']:
        print()
        target = http.client.HTTPConnection(www)
        target.request("GET", (path))
        htmlcontent = target.getresponse()
        data = htmlcontent.read()
        data = data.decode('utf8')
        if i == "bounds":
            pattern = re.compile('bounds-20\d{6}.zip')
        elif i == "sea":
            pattern = re.compile('sea-20\d{12}.zip')
        target.close()

        list = sorted(pattern.findall(data), reverse=True)
        list_new = []
        for i in list:
            if i not in list_new:
                list_new.append(i)
        for i in list_new:
            print("  " + i)

    print()


def fetch_bounds():

    config.read('pygmap3.cfg')
    os.chdir(WORK_DIR + "precomp")

    www = "osm.thkukuk.de"
    path = "/data/"

    for i in ['sea', 'bounds']:
        file_name = config['precomp'][i]
        url = "http://" + www + path + file_name

    if not os.path.exists(file_name):
        print()
        info("download " + url)
        print()
        urlopen = urllib.request.urlopen
        with urlopen(url) as response, open(file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

    os.chdir(WORK_DIR)
