""" Utilities for this plugin.
"""

import inspect
import logging
import json
import importlib

import toml
import bs4

logger = logging.getLogger(__name__)


class IDStore():
    """Load dispatch ID list. Create a new one if not exist.

    Args:
        id_store_path (str): Path to dispatch ID list.
    """

    def __init__(self, id_store_path):
        self._store = {}
        self.id_store_path = id_store_path
        self.saved = False

    def load_from_json(self):
        """Load dispatch IDs from configured JSON file.
        """
        try:
            with open(self.id_store_path) as f:
                self._store = json.load(f)
                logger.debug('Loaded id store: "%r"', self._store)
        except FileNotFoundError:
            self.save()
            logger.debug('Created id store at "%s"', self.id_store_path)

    def load_from_dispatch_config(self, dispatches):
        """Load dispatch IDs from dispatch configurations.

        Args:
            dispatches (dict): Dispatch configuration.
        """

        for name, info in dispatches.items():
            try:
                self._store[name] = info['id']
            except KeyError:
                pass

    def __contains__(self, name):
        """Check existence of an ID.

        Args:
            name (str): Dispatch file name.

        Returns:
            bool: True if contains ID.
        """

        return name in self._store

    def __getitem__(self, name):
        """Get dispatch ID.

        Args:
            name (str): Dispatch file name.

        Returns:
            int: Dispatch ID.
        """
        return self._store[name]

    def __setitem__(self, name, dispatch_id):
        """Add new dispatch ID.

        Args:
            name (str): Dispatch file name.
            dispatch_id (int): Dispatch ID.
        """

        self._store.update({name: dispatch_id})
        self.saved = False

    def save(self):
        """Save ID store into file.
        """

        if self.saved:
            return

        with open(self.id_store_path, 'w') as f:
            json.dump(self._store, f)
            self.saved = True
            logger.debug('Saved id store: "%r"', self._store)


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


def load_dispatch_config(dispatch_config_path):
        """Load dispatch configuration files.

        Args:
            dispatch_config_path (str|list): Dispatch configuration path(s).

        Returns:
            dict: Dispatch configuration.
        """

        if isinstance(dispatch_config_path, str):
            dispatches = toml.load(dispatch_config_path)
            logger.debug('Loaded dispatch config: "%r"', dispatches)
        else:
            dispatches = {}
            for dispatch_config in dispatch_config_path:
                dispatches.update(toml.load(dispatch_config))
                logger.debug('Loaded dispatch config: "%r"', dispatches)

        logger.info('Loaded all dispatch config files')
        return dispatches


def get_new_dispatch_id(html_text):
    """Get new dispatch's ID from respond's HTML.

    Args:
        html_text (str): HTML text of respond.

    Returns:
        int: Dispatch ID.
    """

    soup = bs4.BeautifulSoup(html_text, 'html.parser')

    new_dispatch_url = soup.find(name='p', attrs={'class': 'info'}).a['href']

    dispatch_id = new_dispatch_url.split('id=')[1]

    return int(dispatch_id)
