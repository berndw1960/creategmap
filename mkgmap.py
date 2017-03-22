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

def typ_txt_test():
  global option_typ_file
  global option_style_file

  if (layer == "defaultmap"):
    option_typ_file = " "
    option_style_file = "--style-file=" + WORK_DIR + config['runtime']['mkgmap'] + "/examples/styles/default/ "

  else:
    if os.path.exists(WORK_DIR + "styles/" + layer + "_typ.typ") == True:
      option_typ_file = " " + WORK_DIR + "styles/" + layer + "_typ.typ"
      
    elif os.path.exists(WORK_DIR + "styles/" + layer + "_typ.txt") == True:
      option_typ_file = " " + WORK_DIR + "styles/" + layer + "_typ.txt"
      
    elif os.path.exists(WORK_DIR + "styles/styles_typ.typ") == True and os.path.exists(WORK_DIR + "styles/styles_typ.txt") == True:
      m1 = os.path.getmtime(WORK_DIR + "styles/styles_typ.typ")
      m2 = os.path.getmtime(WORK_DIR + "styles/styles_typ.txt")
      if m1 > m2:
        option_typ_file = " " + WORK_DIR + "styles/styles_typ.typ" 
      elif m2 > m1:
        option_typ_file = " " + WORK_DIR + "styles/styles_typ.txt"
      print()
      printwarning("styles_typ.typ and styles_typ.txt exist, use the newer file")
      print()
      printinfo("typ_file   = " + option_typ_file)
      print()

    elif os.path.exists(WORK_DIR + "styles/styles_typ.typ") == True:
      option_typ_file = " " + WORK_DIR + "styles/styles_typ.typ"

    elif os.path.exists(WORK_DIR + "styles/styles_typ.txt") == True:
      option_typ_file = " " + WORK_DIR + "styles/styles_typ.txt"

    else:
      print()
      printwarning(layer + " build without a typ_file")
      option_typ_file = " "

    option_style_file = " --style-file=" + WORK_DIR + "styles/" + layer + "_style "

  

"""
style check

"""

def check():
  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')
  option_mkgmap_path = WORK_DIR + config['runtime']['mkgmap'] + "/mkgmap.jar "

  global layer
  for layer in config['map_styles']:
    if config['map_styles'][layer] == "yes":
      print()
      print()
      printinfo("checking needed files to build " + layer)
      typ_txt_test()
      print()
      printinfo("typ_file   = " + option_typ_file)
      print()
      printinfo("style_file = " + option_style_file)
      print()
      
      mkgmap_defaultmap_opts = " --x-split-name-index --route --housenumbers --index --nsis "
      mkgmap_style_opts = WORK_DIR + "styles/" + (layer) + "_style/options"
      mkgmap_base_opts = WORK_DIR + "styles/options "
      mkgmap_spec_opts = " --report-similar-arcs --report-dead-ends "
      
      if layer == "defaultmap":
        option_mkgmap_options = mkgmap_defaultmap_opts
        
      elif os.path.exists(mkgmap_style_opts):
        option_mkgmap_options =  mkgmap_style_opts

      else:
        option_mkgmap_options = mkgmap_base_opts
        
      if config['runtime']['use_spec_opts'] == "yes":
        option_mkgmap_spec_opts = mkgmap_spec_opts
      else: 
        option_mkgmap_spec_opts = " "

      os.system("java -jar " + option_mkgmap_path + " -c " + option_mkgmap_options + " --style-file=" + option_style_file + " --check-styles " + option_typ_file)
  print()

  for i in ['styles_typ.typ', 'styles/xstyles_typ.typ', 'splitter.log', 'osmmap.tdb']:
    if os.path.exists(i) == True:
      os.remove(i)

"""
map rendering

"""

def render():
  os.chdir(WORK_DIR)
  config.read('pygmap3.cfg')
  buildmap = config['runtime']['buildmap']
  buildday = config['time_stamp'][buildmap]

  global layer
  for layer in config['map_styles']:

    if config['map_styles'][layer] == "yes":
      os.chdir(WORK_DIR)

      """
      Test for (layer)-dir and remove old data from there
      """

      if os.path.exists(layer) == False:
        os.mkdir(layer)
      else:
        path = layer
        for file in os.listdir(path):
          if os.path.isfile(os.path.join(path, file)):
            try:
              os.remove(os.path.join(path, file))
            except:
              print()
              print('Could not delete', file, 'in', path)

      """
      mkgmap-options
      """

      option_mkgmap_path = WORK_DIR + config['runtime']['mkgmap'] + "/mkgmap.jar "

      if config['runtime']['logging'] == "yes":
        option_mkgmap_logging = " -Dlog.config=" + WORK_DIR + "mkgmap_log.props "
      else:
        option_mkgmap_logging = " "

      if config.has_option('name_tag_list', buildmap) == True:
        option_name_tag_list = " --name-tag-list=" + config['name_tag_list'][buildmap]
      else:
        option_name_tag_list = " --name-tag-list=" + config['name_tag_list']['default']

      bounds_zip = WORK_DIR + "bounds_"+ config['runtime']['bounds'] + ".zip"
      if os.path.exists(bounds_zip):
        option_bounds = " --bounds=" + bounds_zip
      else:
        option_bounds = " --location-autofill=is_in,nearest "
        
      sea_zip = WORK_DIR + "sea_"+ config['runtime']['sea'] + ".zip"
      if os.path.exists(sea_zip):
        option_sea = " --precomp-sea=" + sea_zip + " --generate-sea "
      else:
        option_sea = " --generate-sea=extend-sea-sectors,close-gaps=6000,floodblocker,land-tag=natural=background "
      mkgmap_defaultmap_opts = " --x-split-name-index --route --housenumbers --index --nsis "
      mkgmap_style_opts = WORK_DIR + "styles/" + (layer) + "_style/options"
      mkgmap_base_opts = WORK_DIR + "styles/options "
      mkgmap_spec_opts = " --report-similar-arcs --report-dead-ends "
      
      if layer == "defaultmap":
        option_mkgmap_options = mkgmap_defaultmap_opts
         
      elif os.path.exists(mkgmap_style_opts):
        option_mkgmap_options =  mkgmap_style_opts

      else:
        option_mkgmap_options = mkgmap_base_opts
        
      if config['runtime']['use_spec_opts'] == "yes":
        option_mkgmap_spec_opts = mkgmap_spec_opts
      else: 
        option_mkgmap_spec_opts = " "
      
      typ_txt_test()

      os.chdir(layer)
      print()
      printinfo("building " + layer)

      """
      map rendering
      """
      command_line = ("java -ea " +
                        config['runtime']['ramsize'] +
                        option_mkgmap_logging +
                        " -jar " + option_mkgmap_path +
                        " --keep-going " +
                        " --max-jobs " +
                        option_bounds +
                        option_sea +
                        option_style_file +
                        option_name_tag_list +
                        " --mapname=" + config['mapid'][buildmap] + config[layer]['mapid_ext'] +
                        " --family-id=" + config[layer]['family-id'] +
                        " --product-id=" + config[layer]['product-id'] +
                        " --family-name=" + config[layer]['family-name'] +
                        " --draw-priority=" + config[layer]['draw-priority'] +
                        " --description=" + buildmap + "_" + buildday + "_" + layer +
                        " -c " + option_mkgmap_options +
                        option_mkgmap_spec_opts +
                        " --gmapsupp " +
                        WORK_DIR + "tiles/*.o5m " +
                        option_typ_file)

      if config['runtime']['verbose'] == "yes":
        print()
        printinfo(command_line)
        print()

      os.system(command_line)

      os.chdir(WORK_DIR)

      """
      move gmapsupp.img to unzip_dir as buildmap_(layer)_gmapsupp.img
      """

      unzip_dir = "gps_ready/unzipped/" + buildmap

      bl = buildmap + "_" + layer
      img = unzip_dir + "/" + bl + "_gmapsupp.img"

      if os.path.exists(unzip_dir) == False:
        os.makedirs(unzip_dir)

      if os.path.exists(img) == True:
        os.remove(img)

      shutil.move(layer +"/gmapsupp.img", img)
