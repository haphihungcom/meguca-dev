"""This module handles the scheduling and calling of plugins.
"""


import logging
import logging.config

from apscheduler.schedulers.background import BackgroundScheduler

from meguca import info
from meguca import exceptions
from meguca import plugin
from meguca import utils


logging.config.dictConfig(info.LOGGING_CONFIG)

logger = logging.getLogger(__name__)


class Meguca():
    """Scheduling and plugin handling."""

    def __init__(self, plugins, general_config, plugin_config):
        self.scheduler = BackgroundScheduler()

        self.plugins = plugins

        # Holds general and plugins' configuration
        self.config = {'Meguca': general_config,
                       'Plugins': plugin_config}

        # Holds all service objects
        self.services = {}

        # Holds all data generated and used by plugins
        self.data = {}

    def get_args(self, entry_method, is_stat_plg):
        entry_params = entry_method.__code__.co_varnames
        entry_args = {}

        if 'data' in entry_params:
            entry_args['data'] = plugin.EntryParam(self.data, raise_notyetexist=is_stat_plg)
        if 'config' in entry_params:
            entry_args['config'] = self.config

        for param in entry_params:
            if param in self.services:
                entry_args[param] = self.services[param]

        return entry_args

    def run_plugin(self, plg, entry_method, is_stat_plg=False):
        """Run a plugin.

        Args:
            plg (yapsy.PluginInfo): Plugin metadata object.
            entry_method (str): Name of the entry method.
        """

        entry_method = getattr(plg.plugin_object, entry_method)
        entry_args = self.get_args(entry_method, is_stat_plg)

        return_data = entry_method(**entry_args)

        if return_data:
            self.data.update(return_data)

        logger.info('Run plugin "%s"', plg.name)

    def run_stat_plugins(self):
        """Run all stat plugins."""

        # If a plugin wants to use data not yet created by other plugins,
        # it will be put on queue to run again after the required data
        # become available.
        queue = [plg for plg in self.plugins.get_plugins('Stat')]
        logger.debug('Stat plugins run queue built')

        # Limit the number of iterations through the queue to 2 because
        # after the first iteration, we should have all the data needed by
        # plugins that use non-yet-exist data, the second iteration is to
        # re-run those plugins with the now-exist data.
        for i in range(2):
            for plg in queue:
                try:
                    self.run_plugin(plg, 'run', is_stat_plg=True)
                    logger.info('Run plugin "%s"', plg.name)
                    queue.remove(plg)
                except exceptions.NotYetExist as non_existent_key:
                    if i == 0:
                        logger.debug('Did not find key "%s" in data dict. Put plugin "%s" on rerun queue', plg.name)
                    elif i == 1:
                        raise exceptions.NotFound('Plugin "{}" wanted non-existent key "{}" from data dict.'.format(plg.name, non_existent_key))

    def schedule(self, callable_obj, name, schedule_config, kwargs=None):
        """Schedule a callable.

        Args:
            callable_obj: A callable object.
            name (str): Name to refer to in the scheduler.
            schedule_config (dict): Schedule configuration.
            kwargs (optional): Defaults to None. Arguments to pass to the callable.
        """

        schedule_mode = schedule_config.pop('ScheduleMode')
        self.scheduler.add_job(callable_obj,
                               trigger=schedule_mode,
                               name=name,
                               kwargs=kwargs,
                               coalesce=True,
                               **schedule_config)

        logger.debug('Schedule "%s" with %s and %r', name, schedule_mode, schedule_config)

    def schedule_plugins(self, plg_category):
        """Schedule plugins by category.

        Args:
            plg_category (str): Category name.
        """

        for plg in self.plugins.get_plugins(plg_category):
            identifier = plg.details['Core']['Identifier']
            schedule_config = dict(self.config['Meguca']['PluginSchedule'][identifier])

            self.schedule(self.run_plugin,
                          kwargs={'plg': plg,
                                  'entry_method': 'run'},
                          name=plg.name,
                          schedule_config=schedule_config)

            logger.debug('Scheduled plugin "%s"', plg.name)

        logger.info('Scheduled %s plugins', plg_category)

    def schedule_all(self):
        """Schedule all plugins."""

        self.schedule_plugins('Collector')

        # Stat plugins are run together with the same schedule.
        self.schedule(self.run_stat_plugins,
                      name='Stat plugins',
                      schedule_config=self.config['Meguca']['StatPluginsSchedule'])

        self.schedule_plugins('View')

    def load_services(self):
        """Load service plugins."""

        for plg in self.plugins.get_plugins('Service'):
            args = self.get_args(plg.plugin_object.get, is_stat_plg=False)
            self.services[plg.details['Core']['Identifier']] = plg.plugin_object.get(**args)
            logger.debug('Loaded service "%s"', plg.name)

        logger.info('Loaded all services')

    def prime_run_plugins(self):
        """Prime run collector plugins."""

        for plg in self.plugins.get_plugins('Collector'):
            try:
                self.run_plugin(plg, 'prime_run')
                logging.debug('Prime run plugin "%s"', plg.name)
            except AttributeError:
                logging.debug('Did not find prime_run() in "%s". Skip', plg.name)
                continue

        logger.info('Prime run all plugins')

    def prepare(self):
        """Prepare everything before running."""

        self.load_services()
        self.prime_run_plugins()
        self.schedule_all()

    def run(self):
        """Start the scheduler."""
        self.scheduler.start()
        logger.info('Scheduler started')


def main():
    """Initialize and start Meguca or clean-up and stop it."""

    print('Starting Meguca')
    logger.info('Initialize Meguca')

    general_config = utils.load_config(info.GENERAL_CONFIG_PATH)
    logger.info('Loaded general configuration')

    plugins = plugin.Plugins(info.PLUGIN_DIRECTORY, info.PLUGIN_DESC_EXT)
    plugin_config = plugins.load_plugins()

    meguca = Meguca(plugins, general_config, plugin_config)
    meguca.prepare()
    logger.info('Prepared everything')

    meguca.run()


if __name__ == '__main__':
    main()
