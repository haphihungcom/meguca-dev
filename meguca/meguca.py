"""This module handles the scheduling and calling of plugins.
"""


import logging
import logging.config

from apscheduler.schedulers.background import BackgroundScheduler

from meguca import info
from meguca import exceptions
from meguca import plugin
from meguca import data
from meguca import utils


logging.config.dictConfig(info.LOGGING_CONFIG)

logger = logging.getLogger(__name__)


class Meguca():
    """Scheduling and plugin handling.

        Args:
            plg_manager (plugin.PlgManager): Plugin manager interface.
            general_config (dict): General configuration.
            plg_config (dict): Plugins' configuration.
    """

    def __init__(self, plg_manager, general_config, plg_config):

        self.scheduler = BackgroundScheduler()

        self.plg_manager = plg_manager

        # Holds general and plugins' configuration
        self.config = {'meguca': general_config,
                       'plugins': plg_config}

        # Holds all service objects
        self.services = {}

        # Holds all data generated and used by plugins
        self.data = data.DataStore()

    def get_args(self, entry_method):
        """Get arguments containing dependencies to inject into plugins via entry method.

        Args:
            entry_method (func): Entry method object.

        Returns:
            Entry method arguments.
        """

        entry_params = entry_method.__code__.co_varnames
        entry_args = {}

        if 'data' in entry_params:
            entry_args['data'] = self.data
        if 'config' in entry_params:
            entry_args['config'] = self.config

        for param in entry_params:
            if param in self.services:
                entry_args[param] = self.services[param]

        return entry_args

    def run_plugin(self, plg, entry_method):
        """Run a plugin.

        Args:
            plg (yapsy.PluginInfo): Plugin metadata object.
            entry_method (str): Name of entry method.
        """

        entry_method = getattr(plg.plugin_object, entry_method)
        entry_args = self.get_args(entry_method)

        return_data = entry_method(**entry_args)

        if return_data:
            self.data.update(return_data)

    def run_stat_plugins(self, entry_method):
        """Run stat plugins

        Args:
            entry_method (str): Name of entry method

        Raises:
            exceptions.NotFound: Raises if failed to index data dict.
        """

        # Raises exceptions.NotYetExist instead of exceptions.NotFound
        # if cannot find item in data dict
        self.data.raise_notyetexist = True

        # If a plugin wants to use data not yet created by other plugins,
        # it will be put on queue to run again after the required data
        # become available.
        queue = []
        for plg in self.plg_manager.get_plugins('Stat'):
            if plg.details['Core']['Id'] not in self.config['meguca']['general']['blacklist']:
                    queue.append(plg)
                    logger.debug('Stat plugin "%s" added to queue', plg.name)
            else:
                logger.debug('Stat plugin "%s" blocked from running', plg.name)

        logger.debug('Stat plugins run queue built')

        # Limit the number of iterations through the queue to 2 because
        # after the first iteration, we should have all the data needed by
        # plugins that use non-yet-exist data, the second iteration is to
        # re-run those plugins with the now-exist data.
        for i in range(2):
            for plg in queue:
                try:
                    self.run_plugin(plg, entry_method)
                    logger.info('Run stat plugin "%s"', plg.name)
                    queue.remove(plg)
                except exceptions.NotYetExist as non_existent_key:
                    if i == 0:
                        logger.debug('Did not find key "%s" in data dict. Put plugin "%s" on rerun queue', non_existent_key, plg.name)
                    elif i == 1:
                        raise exceptions.NotFound('Plugin "{}" wanted non-existent key "{}" from data dict.'.format(plg.name, non_existent_key))

        # Return back to raising exceptions.NotFound if cannot find item in data dict
        self.data.raise_notyetexist = False

    def schedule(self, callable_obj, name, schedule_config, kwargs=None):
        """Schedule a callable.

        Args:
            callable_obj: A callable object.
            name (str): Name to refer to in the scheduler.
            schedule_config (dict): Schedule configuration.
            kwargs (optional): Defaults to None. Arguments to pass to the callable.
        """

        schedule_mode = schedule_config.pop('schedule_mode')
        self.scheduler.add_job(callable_obj,
                               trigger=schedule_mode,
                               name=name,
                               kwargs=kwargs,
                               coalesce=True,
                               **schedule_config)

        logger.debug('Scheduled "%s" with "%s" and "%r"',
                     name, schedule_mode, schedule_config)

    def schedule_plugins(self, plg_category):
        """Schedule plugins by category.

        Args:
            plg_category (str): Category name.
        """

        for plg in self.plg_manager.get_plugins(plg_category):
            if plg.details['Core']['Id'] not in self.config['meguca']['general']['blacklist']:
                plg_id = plg.details['Core']['Id']
                schedule_config = dict(self.config['meguca']['plugin_schedule'][plg_id])

                self.schedule(self.run_plugin,
                              kwargs={'plg': plg,
                                      'entry_method': 'run'},
                              name=plg.name,
                              schedule_config=schedule_config)
            else:
                logger.debug('Plugin "%s" blocked from running', plg.name)

        logger.info('Scheduled "%s" plugins', plg_category)

    def schedule_all(self):
        """Schedule all plugins."""

        self.schedule_plugins('Collector')

        # Stat plugins are run together with the same schedule.
        self.schedule(self.run_stat_plugins,
                      kwargs={'entry_method': 'run'},
                      name='Stat plugins',
                      schedule_config=self.config['meguca']['stat_plugins_schedule'])

        self.schedule_plugins('View')

    def load_services(self):
        """Load service plugins."""

        for plg in self.plg_manager.get_plugins('Service'):
            args = self.get_args(plg.plugin_object.get)
            self.services[plg.details['Core']['Id']] = plg.plugin_object.get(**args)
            logger.debug('Loaded service "%s"', plg.name)

        logger.info('Loaded all services')

    def prepare_stat_plugins(self):
        self.run_stat_plugins('prepare')
        logger.debug('Prepared "Stat" plugins')

    def prepare_plugins(self, plg_category):
        """Prepare plugins by category

        Args:
            plg_category (str): Plugin category name.
        """

        for plg in self.plg_manager.get_plugins(plg_category):
            if plg.details['Core']['Id'] not in self.config['meguca']['general']['blacklist']:
                try:
                    self.run_plugin(plg, 'prepare')
                    logger.debug('Initialized plugin "%s"', plg.name)
                except AttributeError:
                    logger.debug('Did not find prepare() in "%s". Skipping', plg.name)
                    continue
            else:
                logger.debug('Plugin "%s" blocked from running', plg.name)

        logger.info('Prepared "%s" plugins', plg_category)

    def prepare(self):
        """Prepare everything before running."""

        self.load_services()
        self.prepare_plugins('Collector')
        self.prepare_stat_plugins()
        self.prepare_plugins('View')

        if not self.config['meguca']['dry_run']['enabled']:
            self.schedule_all()

    def dry_run_plugins(self):
        """Dry run plugins by configured order for testing."""

        plugins = {plg.details['Core']['Id']: plg for plg in self.plg_manager.get_all_plugins()}

        for plg_id in self.config['meguca']['dry_run']['plugins']:
            try:
                plg = plugins[plg_id]
                logger.info('Dry run plugin "%s"', plg.name)
                self.run_plugin(plg, 'dry_run')
            except AttributeError:
                logger.info('Did not find dry_run() in "%s". Skipping', plg.name)
                continue

    def run(self):
        """Start the scheduler or dry run."""

        if self.config['meguca']['dry_run']['enabled']:
            logger.info('Begin dry run')
            self.dry_run_plugins()
        else:
            self.scheduler.start()
            logger.info('Scheduler started')

    def shutdown(self):
        self.scheduler.shutdown()


def main():
    """Initialize and start Meguca or clean-up and stop it."""

    print('Starting Meguca')
    logger.info('Initialize Meguca')

    try:
        general_config = utils.load_config(info.GENERAL_CONFIG_PATH)
        logger.info('Loaded general configuration')
    except FileNotFoundError:
        logger.critical('Could not find general configuration file!')
        raise exceptions.ConfigError('Could not find general configuration file!')

    plg_manager = plugin.PlgManager(info.PLUGIN_DIR_PATH, info.PLUGIN_DESC_EXT)
    plg_config = plg_manager.load_plugins()

    meguca = Meguca(plg_manager, general_config, plg_config)
    meguca.prepare()
    logger.info('Prepared everything')

    meguca.run()

    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        meguca.shutdown()


if __name__ == '__main__':
    main()
