""" Utilities for this plugin.
"""


import inspect
import importlib


def load_funcs(path):
    """Get function objects from a .py file.

    Args:
        path (str): Path to .py file.
    """

    spec = importlib.util.spec_from_file_location('module', path)
    if spec is None:
        return None
    else:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        funcs = inspect.getmembers(module, inspect.isfunction)
        return funcs