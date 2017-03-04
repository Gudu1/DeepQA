# coding: utf8
'''
config module to load configurations
'''

import os
import ConfigParser
import json

CONF_DIR = os.path.dirname(os.path.abspath(__file__)) #返回的是绝对路径，带有文件名


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

    config = ConfigParser.ConfigParser()
    config.read(cf)
    return config


def read_properties():
    '''
    Read Properties from Config File.
    '''
    config = load_config()
    secs = config.sections()
    conf = {}
    for x in secs:
        conf[x] = {y: config.get(x, y) for y in config.options(x)}
    conf['data'] = {'output': CONF_DIR + '/../../dialogues',
                    'output2': CONF_DIR + '/../butterdatas',
                    'output3': CONF_DIR + '/../cobradatas',
                    'pickle': CONF_DIR + '/../pickle',
                    'meta': CONF_DIR + '/../meta',
                    'csvfiles': CONF_DIR + '/../csvfiles'}
    conf['log']['log_path'] = CONF_DIR + '/../logs'
    conf['rule']['blacklist'] = json.loads(config.get("rule", "blacklist"))
    return conf

CONFIG = read_properties()

if __name__ == "__main__":
    conf = read_properties()
    # for x in conf['rule']['blacklist']:
    #     print x
    print conf['rule']['blacklist']
    if 2381 in conf['rule']['blacklist']:
        print 's'
    else:
        print 'x'
