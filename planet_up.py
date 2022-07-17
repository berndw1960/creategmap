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


__version__ = "1.0.0"
__author__ = "Bernd Weigelt"
__copyright__ = "Copyright 2020 Bernd Weigelt"
__license__ = "AGPLv3"
__maintainer__ = "Bernd Weigelt"
__email__ = "weigelt.bernd@web.de"
__status__ = "released"

import os
import argparse


WORK_DIR = os.path.expanduser('~') + "/map_build/"


def info(msg):
    print(("II: " + msg))


def warn(msg):
    print(("WW: " + msg))


def error(msg):
    print(("EE: " + msg))


def checkprg(programmtofind, solutionhint):

    # test if an executable can be found by
    # following $PATH
    # raise message if fails and returns 1
    # on success return 0
    # search follows $PATH

    if os.system("which " + programmtofind) == 1:
        error(programmtofind + " not found")
        print(solutionhint)
        quit()


def is_there(find, solutionhint):

    # test if a file or dir can be found at a predefined place
    # raise message if fails and returns 1
    # on success return 0

    if not os.path.exists(find):
        error(find + " not found")
        print(solutionhint)


hint = ("mkdir " + WORK_DIR)
is_there(WORK_DIR, hint)


os.chdir(WORK_DIR)


for dir in ['planet', 'o5m']:
    if not os.path.exists(dir):
        os.mkdir(dir)


# argparse
parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\

            To create and update a local copy of the OSM planet file

        '''))

parser = argparse.ArgumentParser(

         prog='PROG',
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

args = parser.parse_args()


for tool in ['osmconvert', 'osmupdate', 'osmfilter']:
    hint = tool + " missed, please use mk_osmtools to build it from sources"
    checkprg(tool, hint)


os.chdir(WORK_DIR + "/planet")


if not os.path.exists("planet.osm.pbf") and not os.path.exists("planet.o5m"):
    print()
    info("Download started. Size ~50 Gigabytes... please wait! ")

    os.system("wget http://ftp5.gwdg.de/pub/misc/openstreetmap/"
              + "planet.openstreetmap.org/pbf/planet-latest.osm.pbf")

    conv_hint = ("\n\n Download successful!"
                 + "\n You can now convert the downloaded planet file,"
                 + "\n from OSM.PBF to O5M. "
                 + "\n O5M stores the raw data in a larger file, ~40 percent,"
                 + "\n but extracting data is much faster. Converting the file"
                 + "\n take 15 to 20 minutes on a fast drive."
                 + "\n\n Start converting? [Y|n]")
    conv = input(conv_hint)
    if conv != "n":
        os.system("osmconvert "
                  + "--drop-version "
                  + "--drop-author "
                  + "planet-latest.osm.pbf -o=planet.o5m")
        if os.path.exists("planet.o5m"):
            os.remove("planet-latest.osm.pbf")
    else:
        os.rename("planet-latest.osm.pbf", "planet.osm.pbf")
        print()
        info("if needed in the future, you can convert the planet file"
             + "\n in the planet dir with "
             + "\n\n       'osmconvert planet.osm.pbf -o=planet.o5m' ")


# updating the planet file(s)
print()
info("Now updating the existing planet file(s)")
print()


# to use only one temp dir for osmupdate work one level higher
os.chdir(WORK_DIR)


if os.path.exists("planet/planet.o5m"):
    os.rename("planet/planet.o5m", "planet/planet_temp.o5m")
    os.system(" osmupdate -v --daily --keep-tempfiles "
              + "--drop-version "
              + "--drop-author "
              + "planet/planet_temp.o5m planet/planet.o5m ")
    if os.path.exists("planet/planet.o5m"):
        os.remove("planet/planet_temp.o5m")


if os.path.exists("planet/planet.osm.pbf"):
    os.rename("planet/planet.osm.pbf", "planet/plamet_temp.osm.pbf")
    os.system(" osmupdate -v --daily --keep-tempfiles "
              + "--drop-version "
              + "--drop-author "
              + "planet/planet_temp.osm.pbf planet/planet.osm.pbf")
    if os.path.exists("planet/planet.osm.pbf"):
        os.remove("planet/planet_temp.osm.pbf")


print()


info("Habe fertig!")
quit()
