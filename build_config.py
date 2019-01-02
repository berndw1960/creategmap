#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser


def write_config():
    with open('pygmap3.cfg', 'w') as configfile:
        config.write(configfile)


config = configparser.ConfigParser()


def create():

    # create a default config

    config['DEFAULT'] = {}

    config['osmtools'] = {}
    config['osmtools'] = {'check': 'yes', }

    config['mapid'] = {}
    config['mapid'] = {'next_mapid': '6500', }

    config['java'] = {}
    config['java'] = {'xmx': '-Xmx4G',
                      'xms': '-Xms4G', }

    config['map_styles'] = {}
    config['map_styles'] = {'basemap': 'no',
                            'bikemap': 'no',
                            'carmap': 'no',
                            'defaultmap': 'yes',
                            'oldev': 'no',
                            'fixme': 'no',
                            'bikeroute': 'no',
                            'boundary': 'no',
                            }

    config['defaultmap'] = {}
    config['defaultmap'] = {'product-id': '1',
                            'draw-priority': '10',
                            'mapid_ext': '1001', }

    config['basemap'] = {}
    config['basemap'] = {'product-id': '4',
                         'draw-priority': '10',
                         'mapid_ext': '1001', }

    config['bikemap'] = {}
    config['bikemap'] = {'product-id': '5',
                         'draw-priority': '10',
                         'mapid_ext': '1001', }

    config['carmap'] = {}
    config['carmap'] = {'product-id': '6',
                        'draw-priority': '10',
                        'mapid_ext': '1001', }

    config['boundary'] = {}
    config['boundary'] = {'product-id': '7',
                          'draw-priority': '14',
                          'mapid_ext': '4001', }

    config['bikeroute'] = {}
    config['bikeroute'] = {'product-id': '9',
                           'draw-priority': '16',
                           'mapid_ext': '6001', }

    config['fixme'] = {}
    config['fixme'] = {'product-id': '3',
                       'draw-priority': '16',
                       'mapid_ext': '7001', }

    config['maplevel'] = {}
    config['maplevel'] = {'levels': '0:24,1:23,2:22,3:20,4:18,5:16', }

    config['demtdb'] = {}
    config['demtdb'] = {'demdists': '3314,6628,13256,26512,53024,106048', }

    config['contourlines'] = {}
    config['contourlines'] = {'draw-priority': '16', }

    config['name_tag_list'] = {}
    config['name_tag_list'] = {'default': 'name:en,name:int,name',
                               'dach': 'name:de,name',
                               'germany': 'name:de,name',
                               'bonn': 'name:de,name', }

    write_config()


def update():

    config.read('pygmap3.cfg')

    # add new options

    for i in ['splitter',
              'mkgmap',
              'java',
              'demtdb',
              'maxnodes',
              'mapset']:
        if not config.has_section(i):
            config.add_section(i)

    if not config.has_section('precomp'):
        config.add_section('precomp')
        config.set('precomp', 'sea', 'sea-latest.zip')
        config.set('precomp', 'bounds', 'bounds-latest.zip')

    if config.has_section('bounds'):
        config.remove_section('bounds')

    if not config.has_option('java', 'xmx'):
        config.set('java', 'xmx', '-Xmx4G')

    if not config.has_option('java', 'xms'):
        config.set('java', 'xms', '-Xms4G')

    if not config.has_option('java', 'agh'):
        config.set('java', 'agh', '0')

    if not config.has_option('runtime', 'mapset'):
        config.set('runtime', 'mapset', '0')

    # remove temporary options

    if config.has_option('runtime', 'hourly'):
        config.remove_option('runtime', 'hourly')

    if config.has_option('runtime', 'minutely'):
        config.remove_option('runtime', 'minutely')

    for i in ['mkgmap', 'splitter']:
        if config.has_option(i, 'test'):
            config.remove_option(i, 'test')

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

    if config.has_option('runtime', 'agh'):
        config.remove_option('runtime', 'agh')

    if config.has_option('runtime', 'xmx'):
        config.remove_option('runtime', 'xmx')

    if config.has_option('runtime', 'xms'):
        config.remove_option('runtime', 'xms')

    if not config.has_section('name_tag_list'):
        config.add_section('name_tag_list')
        config.set('name_tag_list', 'default', 'name:en,name:int,name')
    write_config()
