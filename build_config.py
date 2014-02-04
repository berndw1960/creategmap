#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def create():

  """
  create a default config

  """

  import configparser

  config = configparser.ConfigParser()

  config['DEFAULT'] = {}

  config['ramsize'] = {}
  config['ramsize'] = {'ramsize': '-Xmx3G',}
  
  config['verbose'] = {}
  config['verbose'] = {'verbose': 'yes',}
  
  config['mapid'] = {}
  config['mapid'] = {'next_mapid': '6500',}

  config['navmap'] = {}
  config['navmap'] = {'pre_comp': 'yes',
                      'use_sea': 'yes',      
                      'use_bounds': 'yes',
                      'sea':  'latest',
                      'bounds':  'latest',}

  config['splitter'] = {}
  config['splitter'] = {'logging': 'yes',
                        'latest': 'yes',
                        'maxnodes': '1200000',
                        'use_areas': 'no',}

  config['mkgmap'] = {}
  config['mkgmap'] = {'latest': 'yes',
                      'logging': 'no',
                      'check_styles': 'yes',
                      'list_styles': 'no',}

  config['map_styles'] = {}
  config['map_styles'] = {'basemap': 'no',
			  'bikemap': 'no',
                          'fixme': 'no',
                          'default': 'yes',
                          'rrk': 'no',
                          'fzk': 'no',}

  config['basemap'] = {}
  config['basemap'] = {'family-id': '4',
                       'product-id': '45',
                       'family-name': 'Basemap',
                       'draw-priority': '10',
                       'mapid_ext': '1001',}

  config['bikemap'] = {}
  config['bikemap'] = {'family-id': '5',
                       'product-id': '46',
                       'family-name': 'Bikemap',
                       'draw-priority': '10',
                       'mapid_ext': '2001',}

  config['defaultmap'] = {}
  config['defaultmap'] = {'family-id': '6',
                          'product-id': '47',
                          'family-name': 'defaultmap',
                          'draw-priority': '10',
                          'mapid_ext': '5001',}

  config['fzk'] = {}
  config['fzk'] = {'family-id': '6276',
                   'product-id': '1',
                   'family-name': 'Freizeitkarte',
                   'draw-priority': '10',
                   'mapid_ext': '3001',}

  config['rrk'] = {}
  config['rrk'] = {'family-id': '1',
                   'product-id': '1000',
                   'family-name': 'RadReiseKarte',
                   'draw-priority': '10',
                   'mapid_ext': '4001',}

  config['fixme'] = {}
  config['fixme'] = {'family-id': '3',
                     'product-id': '33',
                     'family-name': 'OSM-Fixme',
                     'draw-priority': '16',
                     'mapid_ext': '6001',}

  config['contourlines'] = {}
  config['contourlines'] = {'build': 'no',
                            'draw-priority': '16',}

  config['store_as'] = {}
  config['store_as'] = {'zip_img': 'no',
                        '7z_img': 'no',}

  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

def update():

  """
  update config
  remove unneeded lines
  add new options

  """
  import configparser

  config = configparser.ConfigParser()
  config.read('pygmap3.cfg')

   
  if config.has_section('verbose') == False:
    config['verbose'] = {'verbose': 'no',}
    
  if config.has_section('mapid') == False:
    config['mapid'] = {'next_mapid': '6500',}
 
  if config.has_option('mapid', 'mapid') == True:
    config.remove_option('mapid', 'mapid')

  if config.has_option('splitter', 'use_areas') == False:
    config.set('splitter', 'use_areas', 'no',)
  
  if config.has_section('navmap') == False:
    config['navmap'] = {'pre_comp': 'yes',
                        'use_sea':  'yes',
                        'use_bounds': 'yes',
                        'sea': 'latest',
                        'bounds': 'latest',}
    
  if config.has_option('navmap', 'pre_comp') == False:
    config.set('navmap', 'pre_comp', 'yes',)    

  if config.has_option('navmap', 'use_bounds') == False:
    config.set('navmap', 'use_bounds', 'yes',)
    
  if config.has_option('navmap', 'use_sea') == False:
    config.set('navmap', 'use_sea', 'yes',)    

  if config.has_option('navmap', 'sea') == False:
    config.set('navmap', 'sea', 'latest',)

  if config.has_option('navmap', 'bounds') == False:
    config.set('navmap', 'bounds', 'latest',)

  if config.has_option('map_styles', 'defaultmap') == False:
    config.set('map_styles', 'defaultmap', 'no',)

  if config.has_section('defaultmap') == False:
    config['defaultmap'] = {'family-id': '6',
                          'product-id': '47',
                          'family-name': 'defaultmap',
                          'draw-priority': '10',
                          'mapid_ext': '5001',}

  if config.has_section('contourlines') == True:
    if config.has_option('contourlines', 'draw-priority') == False:
      config.set('contourlines', 'draw-priority', '16',)

  else:
    config['contourlines'] = {'draw-priority': '16', 'build': 'no',}

  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

