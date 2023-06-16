import configparser

def get_config(section, key):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config.get(section, key)
