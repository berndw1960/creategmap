#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
import configparser


def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)


def checkprg(programmtofind, solutionhint):
  """
    test if an executable can be found by
    following $PATH
    raise message if fails and returns 1
    on success return 0
    search follows $PATH
  """

  ExitCode = os.system("which " + programmtofind)

  if ExitCode == 0:
    printinfo(programmtofind + " found")
  else:
    printerror(programmtofind + " not found")
    print(solutionhint)


def is_there(find, solutionhint):
  """
    test if a file or dir can be found at a predefined place
    raise message if fails and returns 1
    on success return 0
  """

  ExitCode = os.path.exists(find)

  if ExitCode == True:
     printinfo(find + " found")
  else:
    printerror(find + " not found")
    print(solutionhint)


WORK_DIR = (os.environ['HOME'] + "/map_build/")

config = configparser.ConfigParser()


def create_cont():

  config.read('pygmap3.cfg')
  buildmap = config.get('runtime', 'buildmap')
  buildday = config.get('runtime', 'buildday')
  cl_dir = ((WORK_DIR) + "contourlines/" + (buildmap) + "/")
  cltemp_dir = ((WORK_DIR) + "contourlines/temp/")

  print("searching for " + (cl_dir) + (buildmap) + "_contourlines_gmapsupp.img")

  ExitCode = os.path.exists((cl_dir) + (buildmap) + "_contourlines_gmapsupp.img")
  if ExitCode == False:
    hint = "Install phyghtmap to create contourlines if needed"
    checkprg("phyghtmap", hint)

  ExitCode = os.path.exists((WORK_DIR) + "mystyles/contourlines_style")
  global mapstyle
  if ExitCode == True:
    mapstyle = "mystyles"
  else:
    ExitCode = os.path.exists((WORK_DIR) + "aiostyles")
    if ExitCode == False:
      os.system("wget -N http://dev.openstreetmap.de/aio/aiostyles.7z")
      os.system("7z x aiostyles.7z -oaiostyles")
      mapstyle = "aiostyles"

  ExitCode = os.path.exists((mapstyle) + "/contourlines_style/lines")
  if ExitCode == False:
    printerror("No contourlines_style found")
    quit()

  os.system("phyghtmap --source=view1,view3,srtm1,srtm3 " +
              " --start-node-id=1 " +
              " --start-way-id=1 " +
              " --max-nodes-per-tile=" + (config.get('splitter', 'maxnodes')) +
              " --max-nodes-per-way=250 " +
              " --jobs=4 " +
              " --pbf " +
              " --no-zero-contour " +
              " -s 20 " +
              " -c 500,100 " +
              " --polygon=poly/" + (buildmap) + ".poly " +
              " -o " +(cltemp_dir) + (buildmap))

  os.chdir(cltemp_dir)
  printinfo("entered " + os.getcwd())

  os.system("java -ea " + (config.get('DEFAULT', 'ramsize')) +
              " -jar " + (config.get('runtime', 'mkgmap_path')) +
              " -c " + (WORK_DIR) + "contourlines.conf " +
              " --style-file=" + (WORK_DIR) + (mapstyle) + "/contourlines_style " +
              " --mapname=" + (config.get('DEFAULT', 'mapid')) + "8001 " +
              " --description=" + (buildday) +
              " --family-name=Contourlines " +
              " --draw-priority=16 " +
              " *.osm.pbf ")

  os.system("cp " + (cltemp_dir) + "gmapsupp.img " + (cl_dir) + (buildmap) + "_contourlines_gmapsupp.img ")


