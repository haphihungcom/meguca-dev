import configparser
import inspect

from apscheduler.schedulers.background import BackgroundScheduler
import yapsy

from . import exceptions
from . import plugin
from .utils import general_utils

GENERAL_CONFIG_FILENAME = "tests/config_for_testing.ini"

class Meguca():
    def __init__(self, config_filename):
        self.scheduler = BackgroundScheduler()

        self.config = {}
        self.config['Meguca'] = general_utils.load_config(config_filename)

        self.plugins = plugin.Plugins(self.config['Meguca']['General']['PluginDirectory'])
        # Plugin-specific config
        self.config['Plugin'] = self.plugins.load_plugins()

        # Hold all data generated and used by plugins
        self.data = {}

        self.prepare()

    def _run_plugin(self, plg, entry_method):
        """Run a plugin.

        :param plg: A yapsy.PluginInfo object
        :param entry_method: Plugin entry method name
        """

        entry = getattr(plg.plugin_object, entry_method)

        # Only pass arguments the entry method requires
        entry_params = dict(inspect.signature(entry).parameters)
        entry_args = {}

        if 'data' in entry_params:
            entry_args['data'] = self.data
        if 'config' in entry_params:
            entry_args['config'] = self.config

        try:
            result = entry(**entry_args)
        except KeyError:
            raise exceptions.DataNotFound()

        # Add returned data to the data dict if the plugin
        # does return data
        if result:
            self.data.update(result)

        print(self.data)

    def _run_stat_plugins(self):
        """Run all stat plugins."""

        # If a plugin wants to use data not yet created by other plugins,
        # it will be put on queue to run again after the required data
        # become available
        queue = [plg for plg in self.plugins.get_plugins('Stat')]

        while queue:
            for plg in queue:
                try:
                    self._run_plugin(plg, 'run')
                    queue.remove(plg)
                except exceptions.DataNotFound:
                    pass

    def _schedule_plugins(self, plg_category, entry_method):
        """Schedule plugins by category.

        :param plg_category: Plugin category name
        :param entry_method: Plugin entry method name
        """

        for plg in self.plugins.get_plugins(plg_category):
            schedule_config = dict(plg.details.items('Scheduling'))
            schedule_mode = schedule_config.pop('schedulemode')
            # Convert all values into int
            if schedule_mode != 'date':
                schedule_config = {k: int(v) for k, v in schedule_config.items()}

            self.scheduler.add_job(self._run_plugin,
                                   trigger=schedule_mode,
                                   name=plg.name,
                                   kwargs={'plg': plg,
                                           'entry_method': entry_method},
                                   coalesce=True,
                                   **schedule_config)

    def _schedule_all(self):
        """Schedule all plugins."""

        self._schedule_plugins('Collector', 'run')

        # Schedule stat plugins which don't have specific scheduling
        # capability

        schedule_config = dict(self.config['Meguca'].items('StatPluginScheduling'))
        schedule_mode = schedule_config.pop('ScheduleMode')
        # Convert all values into int
        if schedule_mode != 'date':
            schedule_config = {k: int(v) for k, v in schedule_config.items()}

        self.scheduler.add_job(self._run_stat_plugins,
                               name='Stat plugins',
                               trigger=schedule_mode,
                               coalesce=True,
                               **schedule_config)

        self._schedule_plugins('View', 'run')

    def prepare(self):
        for plg in self.plugins.get_plugins('Collector'):
            self._run_plugin(plg, 'prime_run')

        self._schedule_all()

    def run(self):
        self.scheduler.start()


def main():
    print('Starting Meguca')
    meguca = Meguca(GENERAL_CONFIG_FILENAME)
    meguca.run()


if __name__ == '__main__':
    main()