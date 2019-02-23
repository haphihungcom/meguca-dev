import time
import configparser
from unittest import mock

import pytest
import freezegun
import apscheduler

from meguca import meguca
from meguca import plugin
from meguca import utils
from meguca import exceptions


@pytest.fixture
def general_config():
    """Standard general config for Meguca."""

    config = {'StatPluginsSchedule': {'ScheduleMode': 'interval',
                                        'seconds': 1}}

    return config


@pytest.fixture
def meguca_dummy_plg(general_config):
    """A Meguca instance with a dummy plugin."""

    plugins = mock.Mock(get_plugins=mock.Mock(return_value=[mock.Mock()]))
    meguca_ins = meguca.Meguca(plugins, general_config, None)

    return meguca_ins


@pytest.mark.usefixtures('mock_plg')
@pytest.fixture
def meguca_standard_plg(mock_plg, general_config):
    """A Meguca instance with a mock plugin which behaves like a real one."""

    plugins = mock.Mock(get_plugins=mock.Mock(return_value=[mock_plg]))
    general_config.update({'PluginSchedule': {'test': {'ScheduleMode': 'interval',
                                                         'seconds': 6}}})

    meguca_ins = meguca.Meguca(plugins, general_config, None)

    return meguca_ins


class TestRunPlugin():
    @pytest.mark.usefixtures('mock_plg')
    def test_run_plugin_with_entry_method_has_no_param(self, mock_plg):
        meguca_ins = meguca.Meguca(mock.Mock(), None, None)

        meguca_ins.run_plugin(mock_plg, 'run')

        assert meguca_ins.data == {'Test': 'Test'}

    @pytest.mark.usefixtures('mock_plg')
    def test_run_plugin_with_entry_method_has_params(self, mock_plg):
        meguca_ins = meguca.Meguca(mock.Mock(), None, None)
        meguca_ins.data = {'TestData': 'Test Data'}

        def stub_run(data):
            return {'Test': data['TestData']}

        mock_plg.plugin_object.run = stub_run

        meguca_ins.run_plugin(mock_plg, 'run')

        assert meguca_ins.data['Test'] == 'Test Data'

    @pytest.mark.usefixtures('mock_plg')
    def test_run_plugin_with_entry_method_has_service_params(self, mock_plg):
        meguca_ins = meguca.Meguca(mock.Mock(), None, None)
        meguca_ins.services = {'service': mock.Mock(return_value='Test')}

        def stub_run(service):
            return {'Test': service()}

        mock_plg.plugin_object.run = stub_run

        meguca_ins.run_plugin(mock_plg, 'run')

        assert meguca_ins.data['Test'] == 'Test'


class TestRunStatPlugins():
    @mock.patch('meguca.meguca.Meguca.run_plugin', side_effect=exceptions.NotFound(''))
    def test_run_stat_plugins_with_plugin_indexes_non_existent_item_of_param(self, run_plugin, meguca_dummy_plg):
        meguca_ins = meguca_dummy_plg

        with pytest.raises(exceptions.NotFound):
            meguca_ins.run_stat_plugins()

    def test_run_stat_plugins_with_plugin_indexes_not_yet_exist_item_of_param(self):
        def stub_run_1():
            return {'TestData1': 'Test Data'}

        def stub_run_2(data):
            return {'TestData2': data['TestData1']}

        mock_plg_1 = mock.Mock(plugin_object=mock.Mock(run=stub_run_1))
        mock_plg_2 = mock.Mock(plugin_object=mock.Mock(run=stub_run_2))
        plugins = mock.Mock(get_plugins=mock.Mock(return_value=[mock_plg_2, mock_plg_1]))
        meguca_ins = meguca.Meguca(plugins, None, None)

        meguca_ins.run_stat_plugins()

        assert meguca_ins.data == {'TestData1': 'Test Data', 'TestData2': 'Test Data'}


class TestPluginSchedulingMethods():
    def test_schedule_with_a_method_with_kwargs(self):
        meguca_ins = meguca.Meguca(mock.Mock(), None, None)
        mock_method = mock.Mock()
        config = {'ScheduleMode': 'interval', 'seconds': 1}

        meguca_ins.schedule(mock_method, kwargs={'Test': 'Test'},
                            name='Test Method',
                            schedule_config=config)

        assert meguca_ins.scheduler.get_jobs()[0].kwargs == {'Test': 'Test'}
        assert str(meguca_ins.scheduler.get_jobs()[0].trigger) == 'interval[0:00:01]'

    def test_schedule_plugins(self, meguca_standard_plg):
        meguca_ins = meguca_standard_plg

        meguca_ins.schedule_plugins('Test')

        assert meguca_ins.scheduler.get_jobs()[0].name == 'Test'

    def test_schedule_all(self, meguca_standard_plg):
        meguca_ins = meguca_standard_plg

        meguca_ins.schedule_all()

        assert meguca_ins.scheduler.get_jobs()[2].name == 'Test'


class TestLoadServices():
    def test_load_services(self):
        def get():
            return 'Test'
        plg_info = configparser.ConfigParser()
        plg_info['Core'] = {'Identifier': 'Test'}
        mock_plg = mock.Mock(plugin_object=mock.Mock(get=get), details=plg_info)
        plugins = mock.Mock(get_plugins=mock.Mock(return_value=[mock_plg]))
        meguca_ins = meguca.Meguca(plugins, None, None)

        meguca_ins.load_services()

        assert meguca_ins.services == {'Test': 'Test'}


class TestRunMeguca():
    @pytest.mark.usefixtures('mock_plg')
    def test_prime_run_plugins(self, meguca_standard_plg):
        meguca_ins = meguca_standard_plg

        meguca_ins.prime_run_plugins()

        assert meguca_ins.data == {'TestPrime': 'Test Prime'}

    def test_run_start_scheduler(self, meguca_dummy_plg):
        meguca_ins = meguca_dummy_plg
        meguca_ins.scheduler = mock.Mock(start=mock.Mock())

        meguca_ins.run()

        meguca_ins.scheduler.start.assert_called()


class TestIntegrationMeguca():
    @freezegun.freeze_time('2018-01-01 00:00:00', tick=True)
    def test_run_meguca_with_real_plugins_and_config(self):
        general_config = utils.load_config('tests/resources/general_config.toml')
        plugins = plugin.Plugins('tests/resources/plugins', 'plugin')
        plugin_config = plugins.load_plugins()

        meguca_ins = meguca.Meguca(plugins, general_config, plugin_config)

        meguca_ins.prepare()
        meguca_ins.run()

        time.sleep(8)

        assert meguca_ins.data == {'Homura': 'TestVal', 'Madoka': 'TestVal',
                                   'Sayaka': 'TestVal', 'SayakaPrimeRun': 'TestVal'}
