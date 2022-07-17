#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import urllib.request
import shutil

WORK_DIR = os.path.expanduser('~') + "/map_build/"


def info(msg):
    print("II: " + msg)


def warn(msg):
    print("WW: " + msg)


def error(msg):
    print("EE: " + msg)


def cities15000():

    # get the geonames for splitter
    file = "cities15000.zip"

    if os.path.exists(file):
        ftime = os.path.getmtime(file)
        curtime = time.time()
        difftime = curtime - ftime
        if difftime > 1741800:
            print()
            warn("cities15000.zip is older then 1 month!")
            os.rename(file, file + ".bak")

    if not os.path.exists(file):
        url = "http://download.geonames.org/export/dump/cities15000.zip"
        # Download the file from `url` and save it locally under `file`:
        try:
            uo = urllib.request.urlopen
            with uo(url) as response, open(file, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            os.remove(file + ".bak")
        except urllib.error.URLError:
            print()
            print(" can't download " + file)
            print()
            if os.path.exists(file + ".bak"):
                os.rename(file + ".bak", file)
