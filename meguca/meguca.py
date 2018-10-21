import configparser
import inspect

from apscheduler.schedulers.background import BackgroundScheduler
import yapsy

from meguca import info
from meguca import exceptions
from meguca import plugin
from meguca import utils

GENERAL_CONFIG_FILENAME = "config/general_config.ini"

class Meguca():
    def __init__(self, plugins, general_config, plugin_config):
        self.scheduler = BackgroundScheduler()

        self.plugins = plugins

        self.config = {'Meguca': general_config,
                       'Plugins': plugin_config}

        # Hold all service objects
        self.services = {}

        # Hold all data generated and used by plugins
        self.data = {}

    def run_plugin(self, plg, entry_method):
        """Run a plugin.

        :param plg: A yapsy.PluginInfo object
        :param entry_method: Plugin entry-point method name
        """

        entrypoint_method = getattr(plg.plugin_object, entry_method)

        # Only pass arguments the entry-point method requires
        entrypoint_params = entrypoint_method.__code__.co_varnames
        entrypoint_args = {}

        if 'data' in entrypoint_params:
            entrypoint_args['data'] = plugin.EntryPointMethodParam(self.data, raise_notyetexist=True)
        if 'config' in entrypoint_params:
            entrypoint_args['config'] = plugin.EntryPointMethodParam(self.config)

        for param in entrypoint_params:
            if param in self.services:
                entrypoint_args[param] = self.services[param]

        result = entrypoint_method(**entrypoint_args)

        # Add returned data to the data dict if the plugin
        # does return data
        if result:
            self.data.update(result)

    def run_stat_plugins(self):
        """Run all stat plugins."""

        # If a plugin wants to use data not yet created by other plugins,
        # it will be put on queue to run again after the required data
        # become available.
        queue = [plg for plg in self.plugins.get_plugins('Stat')]

        # Limit the number of iterations through the queue to 2 because
        # after the first iteration, we should have all the data needed by
        # plugins that use non-yet-exist data, the second iteration is to
        # re-run those plugins with the now-exist data.
        for i in range(2):
            for plg in queue:
                try:
                    self.run_plugin(plg, 'run')
                    queue.remove(plg)
                except exceptions.NotYetExist as non_existent_key:
                    if i == 1:
                        raise exceptions.NotFound('Stat plugin {} requires non-existent item {} from a param'.format(plg.name, non_existent_key))

    def schedule(self, method, name, schedule_config, kwargs={}):
        """Schedule a method with schedule config.

        :param method: Method to schedule
        :param kwargs: A dict that contains keyword arguments to pass to the method
        :param name: Name of the method (optional)
        :param schedule_config: A ConfigParser section object that contains schedule config
        """

        schedule_config = dict(schedule_config)
        schedule_mode = schedule_config.pop('schedulemode')
        # Convert all values into int
        if schedule_mode != 'date':
            schedule_config = {k: int(v) for k, v in schedule_config.items()}

        self.scheduler.add_job(method,
                               trigger=schedule_mode,
                               name=name,
                               kwargs=kwargs,
                               coalesce=True,
                               **schedule_config)

    def schedule_plugins(self, plg_category):
        """Schedule plugins by category.

        :param plg_category: Plugin category name
        """

        for plg in self.plugins.get_plugins(plg_category):
            self.schedule(self.run_plugin,
                           kwargs={'plg': plg,
                                   'entry_method': 'run'},
                           name=plg.name,
                           schedule_config=plg.details.items('Scheduling'))

    def schedule_all(self):
        """Schedule all plugins."""

        self.schedule_plugins('Collector')

        # Schedule stat plugins which don't have scheduling capability for each plugin
        self.schedule(self.run_stat_plugins,
                      name='Stat plugins',
                      schedule_config=self.config['Meguca'].items('StatPluginScheduling'))

        self.schedule_plugins('View')

    def load_services(self):
        for plg in self.plugins.get_plugins('Service'):
            self.services[plg.details['Core']['Identifier']] = plg.plugin_object.get()

    def prime_run_plugins(self):
        for plg in self.plugins.get_plugins('Collector'):
            self.run_plugin(plg, 'prime_run')

    def prepare(self):
        self.load_services()
        self.prime_run_plugins()
        self.schedule_all()

    def run(self):
        self.scheduler.start()


def main():
    print('Starting Meguca')
    general_config = utils.load_config(GENERAL_CONFIG_FILENAME)
    plugins = plugin.Plugins(info.PLUGIN_DIRECTORY)
    plugin_config = plugins.load_plugins()
    meguca = Meguca(plugins, general_config, plugin_config)
    meguca.prepare()
    meguca.run()


if __name__ == '__main__':
    main()