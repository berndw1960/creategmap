#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
version 3 as published by the Free Software Foundation.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.
You should have received a copy of this license along
with this program; if not, see http://www.gnu.org/licenses/.

"""

import os
import time
import urllib.request
import shutil

WORK_DIR = os.environ['HOME'] + "/map_build/"


def printinfo(msg):
    print("II: " + msg)


def printwarning(msg):
    print("WW: " + msg)


def printerror(msg):
    print("EE: " + msg)


def cities15000():

    """
    get the geonames for splitter
    """

    file = (WORK_DIR + "cities15000.zip")

    if os.path.exists(file):
        ftime = os.path.getmtime(file)
        curtime = time.time()
        difftime = curtime - ftime
        if difftime > 1741800:
            print()
            printwarning("""cities15000.zip is older then 1 month!""")
    else:
        url = "http://download.geonames.org/export/dump/cities15000.zip"
        file = "cities15000.zip"
        print()
        printinfo("download " + url)

        # Download the file from `url` and save it locally under `file_name`:
        urlopen = urllib.request.urlopen
        with urlopen(url) as response, open(file, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
