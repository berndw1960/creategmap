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

  config['runtime'] = {}
  config['runtime'] = {'maxnodes': '1600000',
                       'svn': 'no',
                       'logging': 'no',
                       'verbose': 'no',
                       'default': 'bonn',
                       'ramsize': '-Xmx3G',
                       'use_mkgmap_test': ' no',}

  config['map_styles'] = {}
  config['map_styles'] = {'basemap': 'no',
			  'bikemap': 'no',
                          'carmap': 'no',
                          'housenumber': 'no',
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
                       'mapid_ext': '2001',}

  config['carmap'] = {}
  config['carmap'] = {'family-id': '6',
                       'product-id': '46',
                       'family-name': 'Carmap',
                       'draw-priority': '10',
                       'mapid_ext': '3001',}

  config['boundary'] = {}
  config['boundary'] = {'family-id': '7',
                       'product-id': '47',
                       'family-name': 'Boundaries',
                       'draw-priority': '14',
                       'mapid_ext': '4001',}


  config['housenumber'] = {}
  config['housenumber'] = {'family-id': '8',
                       'product-id': '48',
                       'family-name': 'Housenumbers',
                       'draw-priority': '16',
                       'mapid_ext': '5001',}


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
  if config.has_option('navmap', 'use_old_bounds') == False:
    config.set('navmap', 'use_old_bounds', 'no')

  if config.has_option('runtime', 'use_mkgmap_test') == False:
    config.set('runtime', 'use_mkgmap_test', 'no')

  with open('pygmap3.cfg', 'w') as configfile:
    config.write(configfile)

