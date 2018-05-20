#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser

def write_config():
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

config = configparser.ConfigParser()

"""
set prefix for messages

"""

def printinfo(msg):
  print("II: " + msg)

def printwarning(msg):
  print("WW: " + msg)

def printerror(msg):
  print("EE: " + msg)

def create():

  """
  create a default config

  """

  config['DEFAULT'] = {}

  config['osmtools'] = {}
  config['osmtools'] = {'check': 'yes',}
  
  config['mapid'] = {}
  config['mapid'] = {'next_mapid': '6500',}

  config['runtime'] = {}
  config['runtime'] = {'default': 'germany', }
  
  config['java'] = {}
  config['java'] = {'xmx': '-Xmx4G',
                    'xms': '-Xms4G', }

  config['map_styles'] = {}
  config['map_styles'] = {'basemap': 'no',
                          'bikemap': 'no',
                          'carmap': 'no',
                          'fixme': 'no',
                          'bikeroute': 'no',
                          'boundary': 'no',
                          'defaultmap': 'yes',}

  config['defaultmap'] = {}
  config['defaultmap'] = {'family-id': '1',
                          'product-id': '41',
                          'family-name': 'Defaultmap',
                          'draw-priority': '10',
                          'mapid_ext': '1001',}

  config['basemap'] = {}
  config['basemap'] = {'family-id': '4',
                       'product-id': '44',
                       'family-name': 'Basemap',
                       'draw-priority': '10',
                       'mapid_ext': '1001',}

  config['bikemap'] = {}
  config['bikemap'] = {'family-id': '5',
                       'product-id': '45',
                       'family-name': 'Bikemap',
                       'draw-priority': '10',
                       'mapid_ext': '1001',}

  config['carmap'] = {}
  config['carmap'] = {'family-id': '6',
                       'product-id': '46',
                       'family-name': 'Carmap',
                       'draw-priority': '10',
                       'mapid_ext': '1001',}

  config['boundary'] = {}
  config['boundary'] = {'family-id': '7',
                       'product-id': '47',
                       'family-name': 'Boundaries',
                       'draw-priority': '14',
                       'mapid_ext': '4001',}


  config['bikeroute'] = {}
  config['bikeroute'] = {'family-id': '9',
                      'product-id': '49',
                      'family-name': 'Bikeroutes',
                      'draw-priority': '16',
                      'mapid_ext': '6001',}


  config['fixme'] = {}
  config['fixme'] = {'family-id': '3',
                     'product-id': '33',
                     'family-name': 'Fixme',
                     'draw-priority': '16',
                     'mapid_ext': '7001',}
  
  config['maplevel'] = {}
  config['maplevel'] = {'levels': '0:24,1:23,2:22,3:20,4:18,5:16',}
                        
  
  config['demtdb'] = {}
  config['demtdb'] = {'demdists': '3314,6628,13256,26512,53024,106048',}
  
  config['tdblayer'] = {}
  config['tdblayer'] = {'basemap': 'yes',
                        'bikemap': 'yes',
                        'carmap': 'no',}
  

  config['contourlines'] = {}
  config['contourlines'] = {'draw-priority': '16',}
  
  
  config['name_tag_list'] = {}
  config['name_tag_list'] = { 'default': 'name:en,name:int,name',
                              'dach': 'name:de,name',
                              'germany': 'name:de,name',
                              'bonn': 'name:de,name',}
 
  write_config()

def update():
  
  config.read('pygmap3.cfg')

  """
  remove temporary options

  """
  
  if config.has_section('map_styles_backup'):
    print()
    for key in (config['map_styles_backup']):
      config.set('map_styles', key, config['map_styles_backup'][key])
      config.remove_option('map_styles_backup', key)
    config.remove_section('map_styles_backup')
    printinfo("mapstyles restored")

  if config.has_option('runtime', 'hourly'):
    config.remove_option('runtime', 'hourly')
    
  if config.has_option('runtime', 'minutely'):
    config.remove_option('runtime', 'minutely')

  if config.has_option('runtime', 'use_mkgmap_test'):
    config.remove_option('runtime', 'use_mkgmap_test')
  
  if config.has_option('runtime', 'use_old_bounds'):
    config.remove_option('runtime', 'use_old_bounds')
  
  if config.has_option('runtime', 'installer'):
    config.remove_option('runtime', 'installer')

  if config.has_option('runtime', 'use_spec_opts'):
    config.remove_option('runtime', 'use_spec_opts')
  
  if config.has_option('runtime', 'logging'):
    config.remove_option('runtime', 'logging')

  if config.has_option('runtime', 'keep_going'):
    config.remove_option('runtime', 'keep_going')

  if config.has_option('runtime', 'verbose'):
    config.remove_option('runtime', 'verbose')
    
  if config.has_option('runtime', 'maxnodes'):
    config.remove_option('runtime', 'maxnodes')
 
  if config.has_option('runtime', 'agh'):
    config.remove_option('runtime', 'agh')

  """
  add new options

  """
  if config.has_section('java') == False:
    config.add_section('java')
    config.set('java', 'xmx', '-Xmx4G')
    config.set('java', 'xms', '-Xms4G')
  
  if config.has_section('demtdb') == False:
    config.add_section('demtdb')
    
  if config.has_option('demtdb', 'switch_tdb') == False:
    config.set('demtdb', 'switch_tdb', "no")
    
  if config.has_section('maxnodes') == False:
    config.add_section('maxnodes')
  
  if config.has_option('maxnodes','default') == False:
    config.set('maxnodes','default', '1600000')


    
  write_config()  
