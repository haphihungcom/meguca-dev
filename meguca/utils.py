import configparser

def load_config(filename):
    """Get config from an INI file.

    :param filename: Name of config file

    :rtype: A ConfigParser object
    """

    config = configparser.ConfigParser()
    config.read(filename)

    return config