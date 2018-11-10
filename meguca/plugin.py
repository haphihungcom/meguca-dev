import os
import configparser

from yapsy import PluginFileLocator, PluginManager

from meguca import plugin_categories
from meguca import utils
from meguca import exceptions

PLUGIN_CATEGORIES = {
    'Service': plugin_categories.Service,
    'Collector': plugin_categories.Collector,
    'Stat': plugin_categories.Stat,
    'View': plugin_categories.View
}

class Plugins():
    def __init__(self, plugin_dir, plugin_ext):
        plg_analyzer = PluginFileLocator.PluginFileAnalyzerWithInfoFile('locator', plugin_ext)
        plg_locator = PluginFileLocator.PluginFileLocator(analyzers=[plg_analyzer])
        self.plugin_manager = PluginManager.PluginManager(
                              categories_filter=PLUGIN_CATEGORIES,
                              directories_list=[plugin_dir],
                              plugin_locator=plg_locator)

    def load_plugins(self):
        self.plugin_manager.collectPlugins()
        all_plg_config = {}

        for plg in self.plugin_manager.getAllPlugins():
            self.plugin_manager.activatePluginByName(plg.name)

            try:
                plg_config = utils.load_config(plg.details['Core']['ConfigFile'])
                plg.plugin_object.plg_config = plg_config
                all_plg_config[plg.name] = plg_config
            except (IOError, KeyError):
                pass

        return all_plg_config

    def get_plugins(self, category):
        return self.plugin_manager.getPluginsOfCategory(category)


class EntryPointMethodParam():
    """Encapsulate an indexable object to pass as argument
    to the entry-point method of a plugin.

    Args:
        obj (object): An indexable object
        raise_notyetexist (bool, optional): Defaults to False.
            Raise NotYetExist instead of NotFound if cannot index object.
    """

    def __init__(self, obj, raise_notyetexist=False):
        self.obj = obj
        self.raise_notyetexist = raise_notyetexist

    def __getitem__(self, key):
        """Index the object

        Args:
            key (int|str): Index number or key

        Raises:
            exceptions.NotFound: Raise if cannot index object
            exceptions.NotYetExist: Raise if cannot index object when raise_notyetexist is True

        Returns:
            Result of the indexing
        """

        if key not in self.obj:
            if self.raise_notyetexist:
                raise exceptions.NotYetExist(key)
            else:
                raise exceptions.NotFound(key)

        return self.obj[key]