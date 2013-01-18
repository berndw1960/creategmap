#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os

"""
  dirs generate or remove old files
  
"""


def clean_build_dirs():
  
  for dir in ['fixme', 'basemap', 'rrk']:
    ExitCode = os.path.exists(dir)
    if ExitCode == False:
      os.mkdir(dir)
    else:
      path = (dir)
      
  
  for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
      try:
        os.remove(os.path.join(path, file))
      except:
        print('Could not delete', file, 'in', path)
        