import os
import configparser

from yapsy import PluginFileLocator, PluginManager

from meguca import plugin_categories
from meguca import utils
from meguca import exceptions

PLUGIN_CATEGORIES = {
    'Collector': plugin_categories.Collector,
    'Stat': plugin_categories.Stat,
    'View': plugin_categories.View
}

class Plugins():
    def __init__(self, plugin_dir):
        plg_analyzer = PluginFileLocator.PluginFileAnalyzerWithInfoFile('locator', 'plugin')
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
    """Encapsulate an object to pass as argument to the entry-point method of a plugin."""
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, key):
        if key not in self.obj:
            raise exceptions.NotFound()

        return self.obj[key]
