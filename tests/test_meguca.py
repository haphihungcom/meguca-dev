import time
import configparser
from unittest import mock

import pytest
import freezegun

from meguca import meguca
from meguca import plugin
from meguca import utils
from meguca import exceptions


@pytest.fixture
def general_config():
    """Standard general config for Meguca."""

    config = {'general': {'blacklist': []},
              'stat_plugins_schedule': {'schedule_mode': 'interval',
                                        'seconds': 1},
              'dry_run': {'enabled': False,
                          'plugins': []}}

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

    def get_plugins(category=None):
        if category == 'Collector':
            return [mock_plg('Collector1', 'c1'), mock_plg('Collector2', 'c2')]
        elif category == 'Stat':
            return [mock_plg('Stat1', 's1'), mock_plg('Stat2', 's2')]
        elif category == 'View':
            return [mock_plg('View1', 'v1'), mock_plg('View2', 'v2')]
        elif category == 'Service':
            return [mock_plg('Service1', 'sv1', service=True), mock_plg('Service2', 'sv2', service=True)]
        else:
            return [mock_plg('Test1', 't1'), mock_plg('Test2', 't2')]

    plugins = mock.Mock(get_plugins=mock.Mock(side_effect=get_plugins),
                        get_all_plugins=mock.Mock(side_effect=get_plugins))
    general_config.update({'plugin_schedule': {'c1': {'schedule_mode': 'interval',
                                                      'seconds': 6},
                                               'c2': {'schedule_mode': 'interval',
                                                      'seconds': 8},
                                               'v1': {'schedule_mode': 'interval',
                                                      'seconds': 10},
                                               'v2': {'schedule_mode': 'interval',
                                                      'seconds': 12}},
                           'dry_run': { 'plugins': ['t1', 't2']}})

    meguca_ins = meguca.Meguca(plugins, general_config, None)

    return meguca_ins


class TestRunPlugin():
    @pytest.mark.usefixtures('mock_plg')
    def test_run_plugin_with_entry_method_has_no_param(self, mock_plg):
        meguca_ins = meguca.Meguca(mock.Mock(), None, None)

        meguca_ins.run_plugin(mock_plg(), 'run')

        assert meguca_ins.data == {'Test': 'Test'}

    @pytest.mark.usefixtures('mock_plg')
    def test_run_plugin_with_entry_method_has_params(self, mock_plg):
        meguca_ins = meguca.Meguca(mock.Mock(), None, None)
        meguca_ins.data = {'TestData': 'Test Data'}

        def stub_run(data):
            return {'Test': data['TestData']}

        mock_plg = mock_plg()
        mock_plg.plugin_object.run = stub_run

        meguca_ins.run_plugin(mock_plg, 'run')

        assert meguca_ins.data['Test'] == 'Test Data'

    @pytest.mark.usefixtures('mock_plg')
    @mock.patch('meguca.meguca.Meguca.run_plugin', side_effect=exceptions.NotFound(''))
    def test_run_plugin_with_plugin_indexes_non_existent_key_of_data_dict(self, run_plugin, mock_plg):
        meguca_ins = meguca.Meguca(mock.Mock(), None, None)

        with pytest.raises(exceptions.NotFound):
            meguca_ins.run_plugin(mock_plg())

    @pytest.mark.usefixtures('mock_plg')
    def test_run_plugin_with_entry_method_has_service_params(self, mock_plg):
        meguca_ins = meguca.Meguca(mock.Mock(), None, None)
        meguca_ins.services = {'service': mock.Mock(return_value='Test')}

        def stub_run(service):
            return {'Test': service()}

        mock_plg = mock_plg()
        mock_plg.plugin_object.run = stub_run

        meguca_ins.run_plugin(mock_plg, 'run')

        assert meguca_ins.data['Test'] == 'Test'


class TestRunStatPlugins():
    @mock.patch('meguca.meguca.Meguca.run_plugin', side_effect=exceptions.NotFound(''))
    def test_run_stat_plugins_with_plugin_indexes_non_existent_key_of_data_dict(self, run_plugin, meguca_standard_plg):
        meguca_ins = meguca_standard_plg
        meguca_ins.data = mock.Mock()
        type(meguca_ins.data).raise_notyetexist = mock.PropertyMock(return_value=False)

        with pytest.raises(exceptions.NotFound):
            meguca_ins.run_stat_plugins('run')

    def test_run_stat_plugins_with_plugin_indexes_not_yet_exist_key_of_data_dict(self, mock_plg):
        def stub_run_1():
            return {'TestData1': 'Test Data'}

        def stub_run_2(data):
            return {'TestData2': data['TestData1']}

        mock_plg_config_1 = configparser.ConfigParser()
        mock_plg_config_1['Core'] = {'Id': '1'}
        mock_plg_1 = mock.Mock(plugin_object=mock.Mock(run=stub_run_1),
                               details=mock_plg_config_1)

        mock_plg_config_2 = configparser.ConfigParser()
        mock_plg_config_2['Core'] = {'Id': '2'}
        mock_plg_2 = mock.Mock(plugin_object=mock.Mock(run=stub_run_2),
                               details=mock_plg_config_2)

        plugins = mock.Mock(get_plugins=mock.Mock(return_value=[mock_plg_2, mock_plg_1]))
        general_config = {'general': {'blacklist': []}}
        meguca_ins = meguca.Meguca(plugins, general_config, None)
        meguca_ins.data = mock.Mock(__getitem__=mock.Mock(), update=mock.Mock())
        type(meguca_ins.data).raise_notyetexist = mock.PropertyMock(return_value=False)

        meguca_ins.run_stat_plugins('run')

        meguca_ins.data.__getitem__.assert_called_with('TestData1')
        meguca_ins.data.update.assert_called_with({'TestData1': 'Test Data'})


class TestPluginSchedulingMethods():
    def test_schedule_with_a_method_with_kwargs(self):
        meguca_ins = meguca.Meguca(mock.Mock(), None, None)
        mock_method = mock.Mock()
        config = {'schedule_mode': 'interval', 'seconds': 1}

        meguca_ins.schedule(mock_method, kwargs={'Test': 'Test'},
                            name='Test Method',
                            schedule_config=config)

        assert meguca_ins.scheduler.get_jobs()[0].kwargs == {'Test': 'Test'}
        assert str(meguca_ins.scheduler.get_jobs()[0].trigger) == 'interval[0:00:01]'

    def test_schedule_plugins(self, meguca_standard_plg):
        meguca_ins = meguca_standard_plg

        meguca_ins.schedule_plugins('Collector')

        assert meguca_ins.scheduler.get_jobs()[0].name == 'Collector1'

    def test_schedule_all(self, meguca_standard_plg):
        meguca_ins = meguca_standard_plg

        meguca_ins.schedule_all()

        assert meguca_ins.scheduler.get_jobs()[1].name == 'Collector2'
        assert meguca_ins.scheduler.get_jobs()[2].name == 'Stat plugins'
        assert meguca_ins.scheduler.get_jobs()[3].name == 'View1'


class TestLoadServices():
    def test_load_services(self):
        def get():
            return 'Test'
        plg_info = configparser.ConfigParser()
        plg_info['Core'] = {'Id': 'Test'}
        mock_plg = mock.Mock(plugin_object=mock.Mock(get=get), details=plg_info)
        plugins = mock.Mock(get_plugins=mock.Mock(return_value=[mock_plg]))
        meguca_ins = meguca.Meguca(plugins, None, None)

        meguca_ins.load_services()

        assert meguca_ins.services == {'Test': 'Test'}


class TestRunMeguca():
    def test_prepare_plugins(self, meguca_standard_plg):
        meguca_ins = meguca_standard_plg

        meguca_ins.prepare_plugins('Collector')

        assert meguca_ins.data == {'Collector1': 'TestPrep', 'Collector2': 'TestPrep'}

    def test_prepare_stat_plugins(self, meguca_standard_plg):
        meguca_ins = meguca_standard_plg

        meguca_ins.prepare_stat_plugins()

        assert meguca_ins.data['Stat1'] == 'TestPrep'

    def test_prepare(self, meguca_standard_plg):
        meguca_ins = meguca_standard_plg

        meguca_ins.prepare()

        assert meguca_ins.data['Collector2'] == 'TestPrep'
        assert meguca_ins.data['Stat2'] == 'TestPrep'
        assert meguca_ins.data['View1'] == 'TestPrep'
        assert meguca_ins.services['sv1'] == 'TestGet'

    def test_run_start_scheduler(self, meguca_dummy_plg):
        meguca_ins = meguca_dummy_plg
        meguca_ins.scheduler = mock.Mock(start=mock.Mock())

        meguca_ins.run()

        meguca_ins.scheduler.start.assert_called()

    def test_dry_run(self, meguca_standard_plg):
        meguca_ins = meguca_standard_plg
        meguca_ins.config['meguca']['dry_run']['enabled'] = True

        meguca_ins.run()

        assert meguca_ins.data == {'Test1': 'TestDry', 'Test2': 'TestDry'}


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
                                   'Sayaka': 'TestVal', 'SayakaPrep': 'TestVal'}

    def test_dry_run_meguca_real_plugins_and_config(self):
        general_config = utils.load_config('tests/resources/general_config_dryrun.toml')
        plugins = plugin.Plugins('tests/resources/plugins', 'plugin')
        plugin_config = plugins.load_plugins()

        meguca_ins = meguca.Meguca(plugins, general_config, plugin_config)

        meguca_ins.prepare()
        meguca_ins.run()

        assert meguca_ins.data == {'MadokaDry': 'TestVal', 'SayakaPrep': 'TestVal',
                                   'SayakaDry': 'TestVal'}
