#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
import shutil


def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):  print("WW: " + msg)

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

  if os.system("which " + programmtofind) == 0:
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

  if os.path.exists(find) == True:
    printinfo(find + " found")
  else:
    printerror(find + " not found")
    print(solutionhint)


WORK_DIR = (os.environ['HOME'] + "/map_build/")

config = configparser.ConfigParser()


"""
create the contourlines
"""

def create_cont():

  os.chdir(WORK_DIR)

  config.read('pygmap3.cfg')

  buildmap = config['runtime']['buildmap']
  mkgmap_path = WORK_DIR + config['runtime']['mkgmap'] + "/mkgmap.jar "

  cl_dir = "contourlines/" + buildmap + "/"
  cltemp_dir = "cl_temp/"

  for dir in [cltemp_dir, cl_dir]:
    if os.path.exists(dir) == False:
      os.makedirs(dir)

  path = cltemp_dir
  for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
      try:
        os.remove(os.path.join(path, file))
      except:
        print('Could not delete', file, 'in', path)

  print("searching for " + cl_dir + buildmap + "_contourlines_gmapsupp.img")

  if os.path.exists(cl_dir + buildmap + "_contourlines_gmapsupp.img") == False:
    hint = "Install phyghtmap to create contourlines if needed"
    checkprg("phyghtmap", hint)

    global mapstyle
    if os.path.exists("styles/contourlines_style") == True:
      mapstyle = "styles"
    else:
      printerror("contourlines_style not found, please disable it in pygmap3.cfg")

    if os.path.exists(mapstyle + "/contourlines_style/lines") == False:
      printerror("No contourlines_style found")
      quit()
    
    if config['runtime']['use_bbox'] == "yes":
      bound_opts = " -a " + config['bbox'][buildmap].replace(',',':')
    else:
      bound_opts = " --polygon=poly/" + buildmap + ".poly "
      
    if config.has_option('runtime', 'ed_user') == True:
      ed_user_opts = " --earthdata-user=" + config['runtime']['ed_user']
    else:
      ed_user_opts = " " 
      
    if config.has_option('runtime', 'ed_user') == True:
      ed_pwd_opts = " --earthdata-password=" + config['runtime']['ed_pwd']
    else:
      ed_pwd_opts = " "
      
    """
    use phyghtmap to get the raw-data from the internet,
    downloaded files will be stored for later builds
    """
    os.system("phyghtmap --source=view1,view3,srtm1,srtm3 " +
              ed_user_opts +
              ed_pwd_opts +
              " --start-node-id=1 " +
              " --start-way-id=1 " +
              " --max-nodes-per-tile=" + config['runtime']['maxnodes'] +
              " --max-nodes-per-way=250 " +
              " --jobs=4 " +
              " --o5m " +
              " --no-zero-contour " +
              " -s 50 " +
              " -c 500,100 " +
              bound_opts +
              " -o " + cltemp_dir + buildmap)

    """
    contourlines-build with mkgmap
    """

    os.chdir(cltemp_dir)
    printinfo("entered " + os.getcwd())

    os.system("java -ea " + config['runtime']['ramsize'] +
              " -jar " + mkgmap_path +
              " --keep-going " +
              " --max-jobs " +
              " --read-config=" + WORK_DIR + mapstyle + "/contourlines_style/options" +
              " --style-file=" + WORK_DIR + mapstyle + "/contourlines_style" +
              " --mapname=" + config['mapid'][ buildmap] + "8001" +
              " --description=" + buildmap + "_contourlines " +
              " --family-name=Contourlines" +
              " --draw-priority=" + config['contourlines']['draw-priority'] +
              " --gmapsupp " +
              " *.o5m ")

    """
    store the ready contourlines in separated dirs for later use
    """
    
    os.chdir(WORK_DIR)
    shutil.move(cltemp_dir + "gmapsupp.img", cl_dir + buildmap + "_contourlines_gmapsupp.img")

  else:
    printinfo("...found")

