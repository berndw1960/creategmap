#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import shutil

WORK_DIR = os.environ['HOME'] + "/map_build/"

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)

def checkprg(programmtofind, solutionhint):
  ExitCode = os.system("which " + programmtofind)
  if ExitCode == 0:
    printinfo(programmtofind + " found")
  else:
    printerror(programmtofind + " not found")
    print(solutionhint)
    quit()

config = configparser.ConfigParser()

def zip_img():

  os.chdir(WORK_DIR)

  config.read('pygmap3.cfg')

  """
  zipp the images and mv them to separate dirs
  """

  buildmap = config.get('runtime', 'buildmap')
  unzip_dir = (WORK_DIR) + "gps_ready/unzipped/" + (buildmap)
  zip_dir = (WORK_DIR) + "gps_ready/zipped/" + (buildmap)

  ExitCode = os.path.exists(zip_dir)
  if ExitCode == False:
    os.makedirs(zip_dir)

  os.chdir(unzip_dir)

  import zipfile

  try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
  except:
    compression = zipfile.ZIP_STORED
    
  for layer in config['map_styles']:

    if config['map_styles'][(layer)]== "yes":

      bl = (buildmap) + "_" + (layer)

      img = (bl) + "_gmapsupp.img"

      zip_img = (img) + ".zip"

      my_zip_img = zipfile.ZipFile((zip_img), 'w')

      my_zip_img.write((img), compress_type=(compression))

      my_zip_img.close()

      ExitCode = os.path.exists((zip_dir) + "/" + (zip_img))
      if ExitCode == True:
        os.remove((zip_dir) + "/" + (zip_img))

      shutil.move((zip_img), (zip_dir))

def kml():

  os.chdir(WORK_DIR)

  buildmap = config.get('runtime', 'buildmap')
  kml_dir = "gps_ready/zipped/kml/"

  ExitCode = os.path.exists(kml_dir)
  if ExitCode == False:
    os.makedirs(kml_dir)

  ExitCode = os.path.exists("tiles/" + (buildmap) + ".kml")
  if ExitCode == True:
    kml = (kml_dir) + "/" + (buildmap) + ".kml"
    ExitCode = os.path.exists(kml)
    if ExitCode == True:
      os.remove(kml)

    shutil.move("tiles/" + (buildmap) + ".kml", (kml_dir))

def log():

  """
  save the mkgmap-log for errors
  """

  for layer in config['map_styles']:
    if config['map_styles'][(layer)]== "yes":
      os.chdir(WORK_DIR)

      buildmap = config.get('runtime', 'buildmap')
      buildday = config.get('time_stamp', (buildmap))
      log_dir = ("log/mkgmap/" + (buildday) + "/" + (buildmap) + "/" + (layer))

      ExitCode = os.path.exists(log_dir)
      if ExitCode == True:
        shutil.rmtree(log_dir)

      os.chdir(WORK_DIR)

      ExitCode = os.path.exists((layer) + "/mkgmap.log.0")
      if ExitCode == True:
        from shutil import copytree, ignore_patterns
        copytree((layer), (log_dir), ignore=ignore_patterns('*.img', '*.typ', 'osm*'))




