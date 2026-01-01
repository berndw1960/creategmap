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


WORK_DIR = os.path.expanduser('~') + "/map_build/"
config = configparser.ConfigParser()


# download path to thekukuk.de
www = "www.thkukuk.de"
path = "/osm/data/"


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
    print()
    for i in ['sea', 'bounds']:
        dir = os.listdir()
        list = [x for x in dir if x.startswith(i) if x.endswith(".zip")]
        list = sorted(list, reverse=True)
        for i in list:
            print("  " + i)
    print()

    info("files on thkukuk.de (*-latest not listed):")
    for i in ['sea', 'bounds']:
        try:
            target = http.client.HTTPSConnection(www)
            target.request("GET", path)
            htmlcontent = target.getresponse()
            data = htmlcontent.read()
            data = data.decode('utf8')
            target.close()
        except http.client.NotConnected:
            print()
            print(" can't connect to " + target)
            print()
            break

        if i == "bounds":
            pattern = re.compile(r'bounds-20\d{6}.zip')
        elif i == "sea":
            pattern = re.compile(r'sea-20\d{12}.zip')

        data = sorted(pattern.findall(data), reverse=True)
        list_new = []
        for i in data:
            if i not in list_new:
                list_new.append(i)
        for i in list_new:
            print("  " + i)
        print()


def fetch_bounds():

    config.read('pygmap3.cfg')
    os.chdir(WORK_DIR + "precomp")

    for i in ['sea', 'bounds']:
        file = config['precomp'][i]
        url = "http://" + www + path + file

        if not os.path.exists(file):
            print()
            info("download " + url)
            try:
                uo = urllib.request.urlopen
                with uo(url) as response, open(file, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except urllib.error.URLError:
                print()
                print(" can't download " + file)
                print()
                break

    os.chdir(WORK_DIR)
