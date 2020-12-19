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
import configparser
import datetime
import shutil
import build_config


WORK_DIR = (os.environ['HOME'] + "/map_build/")


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

# argparse


parser = argparse.ArgumentParser(
        prog='PROG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\

            To create and update a local copy of the OSM planet file
            There is a option to create new precomp boundaries
            from the planet file, useful if the server thkukuk.de is
            not reachable

        '''))

parser = argparse.ArgumentParser(

         prog='PROG',
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-cb', '--create_bounds', action="store_true",
                    help="create new boundaries")
parser.add_argument('-v', '--verbose', action="store_true",
                    help=False)

args = parser.parse_args()


for tool in ['osmconvert', 'osmupdate', 'osmfilter']:
    hint = tool + " missed, please use mk_osmtools to build it from sources"
    checkprg(tool, hint)


# check for pygmap3.cfg
config = configparser.ConfigParser()


if not os.path.exists("pygmap3.cfg"):
    build_config.create()


config.read('pygmap3.cfg')





if not os.path.exists("planet/planet.osm.pbf"):
    print()
    info("Download started. Size ~50 Gigabytes... please wait! ")
    os.system("wget http://ftp5.gwdg.de/pub/misc/openstreetmap/"
              + "planet.openstreetmap.org/pbf/planet-latest.osm.pbf")
    os.rename("planet/planet-latest.osm.pbf", "planet/planet.osm.pbf")
    os.chdir(WORK_DIR)


command_line = (" osmupdate -v --daily --keep-tempfiles "
                + "planet/planet.osm.pbf planet/planet_new.osm.pbf")


if args.verbose:
    print()
    print(command_line)
    print()


os.system(command_line)

os.chdir("planet/")
print()


if os.path.exists("planet_new.osm.pbf"):
    os.rename("planet.osm.pbf", "planet_temp.osm.pbf")
    os.rename("planet_new.osm.pbf", "planet.osm.pbf")
    if os.path.exists("planet.osm.pbf"):
        os.remove("planet_temp.osm.pbf")


# create the bounds from planet


if args.create_bounds:

    command_line = ("osmfilter -v planet.osm.pbf  --keep-nodes= "
                    + "--keep-ways-relations='boundary=administrative "
                    + "=postal_code postal_code=' "
                    + "--drop-tags='created_by= source= building= "
                    + "=highway maxspeed= surface= oneway= note= natural="
                    + " lit=' -o=bounds_data.o5m")

    if args.verbose:
        print()
        print(command_line)
        print()

    os.system(command_line)

    print()

    mkgmap = WORK_DIR + config['mkgmap']['rev'] + "/mkgmap.jar "

    if config['java']['agh'] == "1":
        heap = " -XX:+AggressiveHeap "
    else:
        heap = config['java']['xmx'] + ' ' + config['java']['xms']

    command_line = ("java -ea " +
                    heap +
                    " -cp " +
                    mkgmap +
                    " uk.me.parabola.mkgmap.reader.osm."
                    + "boundary.BoundaryPreprocessor "
                    + "bounds_data.o5m bounds ")
    if args.verbose:
        print()
        print(command_line)
        print()

    os.system(command_line)

    print()

    # set date for info
    today = datetime.datetime.now()
    DATE = today.strftime('%Y%m%d')
    zipf = "bounds-" + DATE
    shutil.make_archive(zipf, 'zip', "bounds")
    shutil.move(zipf + ".zip", WORK_DIR + "precomp")
    shutil.rmtree("bounds")
    os.remove("bounds_data.o5m")

    os.chdir(WORK_DIR)

info("Habe fertig!")
quit()
