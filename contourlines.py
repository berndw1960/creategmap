#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
import configparser


WORK_DIR = (os.environ['HOME'] + "/map_build/")

config = configparser.ConfigParser()
config.read('pygmap3.cfg')

def create_cont():
  buildmap = config.get('runtime', 'buildmap')
  buildday = config.get('runtime', 'buildday')
  cl_dir = ((WORK_DIR) + "contourlines/" + (buildmap) + "/")
  cltemp_dir = ((WORK_DIR) + "contourlines/temp/")
  print("searching for " + (cl_dir) + (buildmap) + "_contourlines_gmapsupp.img")
  ExitCode = os.path.exists((cl_dir) + (buildmap) + "_contourlines_gmapsupp.img")
  if ExitCode == False:
    hint = "Install phyghtmap to create contourlines if needed"
    checkprg("phyghtmap", hint)
    
    os.system("phyghtmap --source=view1,view3,srtm1,srtm3 " + 
              " --start-node-id=1 " +
              " --start-way-id=1 " +
              " --max-nodes-per-tile=" + (MAXNODES) +
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
              " -jar " + (mkgmap) +                    
              " -c " + (WORK_DIR) + "contourlines.conf " +
              " --style-file=" + (WORK_DIR) + (mapstyle) + "/contourlines_style " +
              " --mapname=" + (config.get('DEFAULT', 'mapid')) + "8001 " +
              " --description=" + (buildday) +
              " --family-name=Contourlines " +
              " --draw-priority=16 " + 
              " *.osm.pbf ")
  
    os.system("cp " + (cltemp_dir) + "gmapsupp.img " + (cl_dir) + (buildmap) + "_contourlines_gmapsupp.img ") 
  else:
    print("...found")
  


