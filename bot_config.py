from configparser import ConfigParser


def config_connect(path):
    _config = ConfigParser()
    _config.read(path)
    return _config.get('Token', 'token')


class ConfigBot(ConfigParser):
    def __init__(self):
        ConfigParser.__init__(self)
        self.config = ConfigParser()
        self.config.read('config.ini')

    def get_option(self, section, option):
        return self.config[section][option]

    def get_dict(self, section):
        return dict(self.config[section])