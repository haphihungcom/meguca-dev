"""This module handles loading plugins and contains utilities
to interact with the plugins.
"""


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
    """Load plugins and provide an interface to access them.

        Args:
            plugin_dir (str): Directory to find plugin description files.
            plugin_ext (str): Plugin description file extension name.
        """

    def __init__(self, plugin_dir, plugin_ext):
        plg_analyzer = PluginFileLocator.PluginFileAnalyzerWithInfoFile('locator', plugin_ext)
        plg_locator = PluginFileLocator.PluginFileLocator(analyzers=[plg_analyzer])
        self.plugin_manager = PluginManager.PluginManager(categories_filter=PLUGIN_CATEGORIES,
                                                          directories_list=[plugin_dir],
                                                          plugin_locator=plg_locator)

    def load_plugins(self):
        """Load plugins.

        Returns:
            dict: Plugins' configuration.
        """

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
        """Get plugins by category

        Args:
            category (str): Category name

        Returns:
            list: Plugin metadata objects.
        """

        return self.plugin_manager.getPluginsOfCategory(category)
