import configparser

def get_yes_no(question):
    """"""


def load_config(filename):
    """Get config from an INI file.

    :param filename: Name of config file

    :rtype: A ConfigParser object
    """

    config = configparser.ConfigParser()
    config.optionxform = str

    f = open(filename)
    config.read(filename)

    return config