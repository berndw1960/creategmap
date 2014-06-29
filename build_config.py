#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def create():

  """
  create a default config

  """

  import configparser

  config = configparser.ConfigParser()

  config['DEFAULT'] = {}

  config['osmtools'] = {}
  config['osmtools'] = {'check': 'yes',}

  config['mapid'] = {}
  config['mapid'] = {'next_mapid': '6500',}

  config['navmap'] = {}
  config['navmap'] = {'pre_comp': 'yes',
                      'use_sea': 'yes',
                      'use_bounds': 'yes',}

  config['runtime'] = {}
  config['runtime'] = {'maxnodes': '1600000',
                       'use_areas': 'no',
                       'svn': 'no',
                       'logging': 'no',
                       'verbose': 'no',
                       'default': 'germany',
                       'ramsize': '-Xmx3G',}

  config['map_styles'] = {}
  config['map_styles'] = {'basemap': 'no',
			  'bikemap': 'no',
                          'carmap': 'no',
                          'housenumber': 'no',
                          'fixme': 'no',
                          'defaultmap': 'yes',}

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

  config['carmap'] = {}
  config['carmap'] = {'family-id': '6',
                       'product-id': '47',
                       'family-name': 'Carmap',
                       'draw-priority': '10',
                       'mapid_ext': '3001',}

  config['housenumber'] = {}
  config['housenumber'] = {'family-id': '7',
                       'product-id': '48',
                       'family-name': 'Housenumbers',
                       'draw-priority': '16',
                       'mapid_ext': '6001',}

  config['defaultmap'] = {}
  config['defaultmap'] = {'family-id': '9',
                          'product-id': '50',
                          'family-name': 'defaultmap',
                          'draw-priority': '10',
                          'mapid_ext': '5001',}

  config['fixme'] = {}
  config['fixme'] = {'family-id': '3',
                     'product-id': '33',
                     'family-name': 'OSM-Fixme',
                     'draw-priority': '16',
                     'mapid_ext': '6001',}

  config['contourlines'] = {}
  config['contourlines'] = {'draw-priority': '16',}

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

  if ('runtime' in config) == False:
    config.add_section('runtime')

  if config.has_option('runtime', 'default') == False:
    if config.has_option('mapset', 'default') == True:
      config.set('runtime', 'default', config.get('mapset', 'default'))
      config.remove_option('mapset', 'default')
    else:
      config.set('runtime', 'default', 'germany')

  if config.has_option('runtime', 'ramsize') == False:
    config.set('runtime', 'ramsize', '-Xmx3G')

  if config.has_option('runtime', 'svn') == False:
    config.set('runtime', 'svn', 'no')

  if config.has_option('runtime', 'logging') == False:
    config.set('runtime', 'logging', 'no')

  if config.has_option('runtime', 'verbose') == False:
    config.set('runtime', 'verbose', 'no')

  if config.has_option('runtime', 'maxnodes') == False:
    config.set('runtime', 'maxnodes', '1600000')

  if config.has_option('runtime', 'use_areas') == False:
    config.set('runtime', 'use_areas', 'no')

  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

