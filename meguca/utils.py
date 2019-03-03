"""A few utilities.
"""


import logging

import toml


def load_config(filename):
    """Load configuration from a TOML file.

    Args:
        filename (str): File name.

    Returns:
        dict: Configuration as a dictionary.
    """

    return toml.load(filename)


def canonical(name):
    """Turn a name into canonical form with no underscore or upper case.

    Args:
        name (str): A name

    Returns:
        str: Canonicalized name.
    """

    return name.lower().replace('_', ' ')
