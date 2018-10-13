import time
import configparser
from unittest import mock

import pytest
import freezegun
import apscheduler

from meguca import meguca
from meguca import exceptions


def meguca_config():
    """Config for testing."""

    config = configparser.ConfigParser()
    config['General'] = {'PluginDirectory': 'Test'}
    config['StatPluginScheduling'] = {'ScheduleMode': 'interval',
                                      'seconds': '1'}

    return config


@mock.patch('meguca.meguca.Meguca.prepare')
@mock.patch('meguca.utils.load_config', return_value=meguca_config())
@mock.patch('meguca.plugin.Plugins.load_plugins', mock.Mock(return_value='Test'))
class TestRunPlugin():
    @pytest.mark.usefixtures('mocked_plg')
    def test_run_plugin_with_entrypoint_method_has_no_param(self, mocked_plugins,
                                                            mocked_load_config, mocked_plg):
        meguca_ins = meguca.Meguca('')

        meguca_ins.run_plugin(mocked_plg, 'run')

        assert meguca_ins.data == {'Test': 'Test'}

    @pytest.mark.usefixtures('mocked_plg')
    def test_run_plugin_with_entrypoint_method_has_params(self, mocked_load_plugins,
                                                          mocked_load_config, mocked_plg):
        meguca_ins = meguca.Meguca('')
        meguca_ins.data = {'TestData': 'Test Data'}

        def stub_run(data):
            return {'Test': data['TestData']}

        mocked_plg.plugin_object.run = stub_run

        meguca_ins.run_plugin(mocked_plg, 'run')

        assert meguca_ins.data['Test'] == 'Test Data'


@mock.patch('meguca.utils.load_config', return_value=meguca_config())
@mock.patch('meguca.meguca.Meguca.prepare')
@mock.patch('meguca.plugin.Plugins.load_plugins')
@mock.patch('meguca.plugin.Plugins.get_plugins', return_value=[mock.Mock()])
class TestRunStatPlugins():
    @mock.patch('meguca.meguca.Meguca.run_plugin', side_effect=exceptions.NotFound(''))
    def test_run_stat_plugins_with_plugin_accesses_non_existent_item_of_param(self, mocked_run_plugin,
                                                                 mocked_get_plugins, mocked_load_plugins,
                                                                 mocked_prepare, mocked_load_config):
        meguca_ins = meguca.Meguca('')

        with pytest.raises(exceptions.NotFound):
            meguca_ins.run_stat_plugins()

    def test_run_stat_plugins_with_plugin_accesses_not_yet_exist_item_of_param(self, mocked_get_plugins,
                                                                        mocked_load_plugins, mocked_prepare,
                                                                        mocked_load_config):
        with mock.patch('meguca.plugin.Plugins.get_plugins') as mocked_get_plugins:
            meguca_ins = meguca.Meguca('')

            def stub_run_1():
                return {'TestData1': 'Test Data'}

            def stub_run_2(data):
                return {'TestData2': data['TestData1']}

            mocked_plg_1 = mock.Mock(plugin_object=mock.Mock(run=stub_run_1))
            mocked_plg_2 = mock.Mock(plugin_object=mock.Mock(run=stub_run_2))
            mocked_get_plugins.return_value = [mocked_plg_2, mocked_plg_1]

            meguca_ins.run_stat_plugins()

            assert meguca_ins.data == {'TestData1': 'Test Data', 'TestData2': 'Test Data'}


@mock.patch('meguca.utils.load_config', return_value=meguca_config())
@mock.patch('meguca.meguca.Meguca.prepare')
@mock.patch('meguca.plugin.Plugins.load_plugins')
class TestPluginSchedulingMethods():
    def test_schedule_with_a_method_with_kwargs(self, mocked_load_config,
                                                mocked_prepare, mocked_load_plugins):
        meguca_ins = meguca.Meguca('')
        mocked_method = mock.Mock()
        schedule_config = configparser.ConfigParser()
        schedule_config['Scheduling'] = {'ScheduleMode': 'interval',
                                         'seconds': '1'}

        meguca_ins.schedule(mocked_method, kwargs={'Test': 'Test'},
                            name='Test Method',
                            schedule_config=schedule_config.items('Scheduling'))

        assert meguca_ins.scheduler.get_jobs()[0].kwargs == {'Test': 'Test'}
        assert str(meguca_ins.scheduler.get_jobs()[0].trigger) == 'interval[0:00:01]'

    @pytest.mark.usefixtures('mocked_plg')
    def test_schedule_plugins(self, mocked_load_plugins,
                              mocked_prepare, mocked_load_config, mocked_plg):
        with mock.patch('meguca.plugin.Plugins.get_plugins') as mocked_get_plugins:
            meguca_ins = meguca.Meguca('')
            mocked_get_plugins.return_value = [mocked_plg]

            meguca_ins.schedule_plugins('Test')

            assert meguca_ins.scheduler.get_jobs()[0].name == 'Test'

    @pytest.mark.usefixtures('mocked_plg')
    def test_schedule_all(self, mocked_load_plugins, mocked_prepare,
                          mocked_load_config, mocked_plg):
        with mock.patch('meguca.plugin.Plugins.get_plugins') as mocked_get_plugins:
            meguca_ins = meguca.Meguca('')
            mocked_get_plugins.return_value = [mocked_plg]

            meguca_ins.schedule_all()

            assert meguca_ins.scheduler.get_jobs()[2].name == 'Test'


@mock.patch('meguca.utils.load_config', return_value=meguca_config())
@mock.patch('meguca.plugin.Plugins.load_plugins')
class TestRunMeguca():
    @pytest.mark.usefixtures('mocked_plg')
    def test_prepare_calls_plugin_prime_run(self, mocked_load_plugins, mocked_load_config,
                                            mocked_plg):
        with mock.patch('meguca.plugin.Plugins.get_plugins') as mocked_get_plugins:
            meguca_ins = meguca.Meguca('')
            mocked_get_plugins.return_value = [mocked_plg]

            meguca_ins.prepare()

            assert meguca_ins.data == {'TestPrime': 'Test Prime'}

    @mock.patch('meguca.meguca.Meguca.prepare')
    def test_run(self, mocked_prepare, mocked_load_plugins, mocked_load_config):
        meguca_ins = meguca.Meguca('')
        meguca_ins.scheduler = mock.Mock(start=mock.Mock())

        meguca_ins.run()

        meguca_ins.scheduler.start.assert_called()


class TestIntegrationMeguca():
    @freezegun.freeze_time('2018-01-01 00:00:00', tick=True)
    def test_run_meguca_with_real_plugin_and_config(self):
        meguca_ins = meguca.Meguca('tests/real_resources/general_config.ini')

        meguca_ins.run()

        time.sleep(8)

        assert meguca_ins.data == {'Homura': 'TestVal', 'Madoka': 'TestVal',
                                   'Sayaka': 'TestVal', 'SayakaPrimeRun': 'TestVal'}