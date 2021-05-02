import configparser

def build_cfg():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'x1'       : '0',
                        'y1'        : '0',
                        'x2'        : '1920',
                        'y2'        : '1080',
                        'difference': '2',
                        'type_speed': '0.05',
                        'cmd_speed' : '0.5'}
    config['cust']    = {'x1'       : '0',
                        'y1'        : '0',
                        'x2'        : '1920',
                        'y2'        : '1080',
                        'difference': '2',
                        'type_speed': '0.05',
                        'cmd_speed' : '0.5',
                        'build_model': '0'}
    with open('cfg/cfg.ini', 'w') as configfile:
        config.write(configfile)

def load_cfg():
    config = configparser.ConfigParser()
    config.read('cfg/cfg.ini')
    # for key in config['DEFAULT']:
    #     print(key)
    #     print(config['DEFAULT'][key])
    return config

def modify_cfg(key, value):
    config = configparser.ConfigParser()
    config.read('cfg/cfg.ini')
    config['cust'][key] = str(value)
    with open('cfg/cfg.ini', 'w') as configfile:
        config.write(configfile)

if __name__ == '__main__':
    build_cfg()