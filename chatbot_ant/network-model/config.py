# coding: utf8
'''
config module to load configurations
'''

import os
import configparser
import json

CONF_DIR = os.path.dirname(os.path.abspath(__file__))

def get_cfg_dir():
    '''
    Get cfg dir
    '''
    if not os.path.exists(CONF_DIR):
        os.mkdir(CONF_DIR)
    return CONF_DIR

def get_cfg_path():
    '''
    Get cfg path
    '''
    return os.path.join(get_cfg_dir(), 'config.ini')


def load_config():
    '''
    Load configurations
    '''
    cf = get_cfg_path()
    if not os.path.exists(cf):
        f = open(cf, 'w')
        f.close()

    config = configparser.ConfigParser()
    config.read(cf)
    return config

def get_properties():
    '''
    Read Properties from Config File.
    '''
    config = load_config()
    secs = config.sections()
    conf = {}
    for x in secs:
        conf[x] = {y: config.get(x, y) for y in config.options(x)}
    return conf

if __name__ == "__main__":
    print(get_properties())

