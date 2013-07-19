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


config = configparser.ConfigParser()

def zipp():

  os.chdir(WORK_DIR)

  config.read('pygmap3.cfg')


  """
  zipp the images and mv them to separate dirs
  """

  for layer in config['map_styles']:

    if config['map_styles'][(layer)]== "yes":

      buildmap = config.get('runtime', 'buildmap')
      bl = (buildmap) + "_" + (layer)
      unzip_dir = "gps_ready/unzipped/" + (buildmap)
      zip_dir = "gps_ready/zipped/" + (buildmap)
      img = (unzip_dir) + "/" + (bl) + "_gmapsupp.img"

      ExitCode = os.path.exists(zip_dir)
      if ExitCode == False:
        os.makedirs(zip_dir)

      if config.get('store_as', 'zip_img') == "yes":
        zip_img = (bl) + "_gmapsupp.img.zip"

        ExitCode = os.path.exists((zip_dir) + "/" + (zip_img))
        if ExitCode == True:
          os.remove((zip_dir) + "/" + (zip_img))

        os.system(("zip ") + (zip_dir) + "/" + (zip_img) + " " + (img))


      if config.get('store_as', '7z_img') == "yes":
        sevenz_img = (bl) + "_gmapsupp.img.7z"

        ExitCode = os.path.exists((zip_dir) + "/" + (sevenz_img))
        if ExitCode == True:
          os.remove((zip_dir) + "/" + (sevenz_img))

        os.system(("7z a ") + (zip_dir) + "/" + (sevenz_img) + " " + (img))

def kml():

  os.chdir(WORK_DIR)

  buildmap = config.get('runtime', 'buildmap')
  zip_dir = "gps_ready/zipped/" + (buildmap)

  ExitCode = os.path.exists("tiles/" + (buildmap) + ".kml")
  if ExitCode == True:
    kml = (zip_dir) + "/" + (buildmap) + ".kml"
    ExitCode = os.path.exists(kml)
    if ExitCode == True:
      os.remove(kml)

    shutil.move("tiles/" + (buildmap) + ".kml", (zip_dir))

def log():

  """
  save the mkgmap-log for errors
  """


  if config.get('mkgmap', 'logging') == "yes":
    for layer in config['map_styles']:
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




