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
  if os.system("which " + programmtofind) == 0:
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

  buildmap = config['runtime']['buildmap']
  unzip_dir = WORK_DIR + "gps_ready/unzipped/" + buildmap
  zip_dir = WORK_DIR + "gps_ready/zipped/" + buildmap

  if os.path.exists(zip_dir) == False:
    os.makedirs(zip_dir)

  os.chdir(unzip_dir)

  import zipfile

  for layer in config['map_styles']:

    if config['map_styles'][layer]== "yes":
      bl = buildmap + "_" + layer
      img = bl + "_gmapsupp.img"
      zip_img = img + ".zip"
      my_zip_img = zipfile.ZipFile(zip_img, 'w', allowZip64=True)
      my_zip_img.write(img, compress_type=zipfile.ZIP_DEFLATED)
      my_zip_img.close()

      if os.path.exists(zip_dir + "/" + zip_img) == True:
        os.remove(zip_dir + "/" + zip_img)

      shutil.move(zip_img, zip_dir)
      
      os.remove(unzip_dir + "/" + img)
  
  os.chdir(WORK_DIR)
  if os.path.exists(unzip_dir):
    shutil.rmtree(unzip_dir)
    
def kml():

  os.chdir(WORK_DIR)

  buildmap = config['runtime']['buildmap']
  kml_dir = "gps_ready/zipped/" + buildmap

  if os.path.exists(kml_dir) == False:
    os.makedirs(kml_dir)

  if os.path.exists("tiles/" + buildmap + ".kml") == True:
    kml = kml_dir + "/" + buildmap + ".kml"
    if os.path.exists(kml) == True:
      os.remove(kml)

    shutil.move("tiles/" + buildmap + ".kml", kml_dir)

def log():

  """
  save the mkgmap-log for errors
  """
  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')

  for layer in config['map_styles']:
    if config['map_styles'][layer]== "yes":

      buildmap = config['runtime']['buildmap']
      buildday = config['time_stamp'][buildmap]
      log_dir = ("log/mkgmap/" + buildmap + "/" + layer + "/" + buildday)

      if os.path.exists(log_dir) == True:
        shutil.rmtree(log_dir)

      if os.path.exists(layer + "/mkgmap.log.0") == True:

        from shutil import copytree, ignore_patterns
        copytree(layer, log_dir, ignore=ignore_patterns('*.img', '*.typ', 'osm*'))




