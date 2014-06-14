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

  config['osmtools'] = {}
  config['osmtools'] = {'check': 'yes',}

  config['mapset'] = {}
  config['mapset'] = {'default': 'dach',}

  config['mapid'] = {}
  config['mapid'] = {'next_mapid': '6500',}

  config['navmap'] = {}
  config['navmap'] = {'pre_comp': 'yes',
                      'use_sea': 'yes',
                      'use_bounds': 'yes',}

  config['splitter'] = {}
  config['splitter'] = {'maxnodes': '1600000',
                        'use_areas': 'no',}

  config['mkgmap'] = {}
  config['mkgmap'] = {'logging': 'no',}

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
    
  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

