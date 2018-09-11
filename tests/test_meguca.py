import time
from unittest import mock

import pytest
import freezegun

from meguca import meguca
from meguca import exceptions

@mock.patch('meguca.meguca.Meguca.prepare')
@mock.patch('meguca.utils.load_config', return_value={'General': {'PluginDirectory': 'Test'}})
@mock.patch('meguca.plugin.Plugins.load_plugins', mock.Mock(return_value='Test'))
class TestRunPlugin():
    def test_run_plugin_with_entrypoint_method_has_no_param(self, mocked_plugins, mocked_load_config):
        meguca_ins = meguca.Meguca('')
        mocked_plg_obj = mock.Mock(run=mock.Mock(return_value={'Test': 'Test'},
                                                 __code__=mock.Mock(co_varnames=())))
        mocked_plg = mock.Mock(plugin_object=mocked_plg_obj)

        meguca_ins._run_plugin(mocked_plg, 'run')

        mocked_plg_obj.run.assert_called_with()
        assert meguca_ins.data == {'Test': 'Test'}

    def test_run_plugin_with_entrypoint_method_has_params(self, mocked_load_plugins, mocked_load_config):
        meguca_ins = meguca.Meguca('')
        meguca_ins.data = {'TestData': 'Test Data'}

        def stub_run(data):
            return {'Test': data['TestData']}

        mocked_plg_obj = mock.Mock(run=stub_run)
        mocked_plg = mock.Mock(plugin_object=mocked_plg_obj)

        meguca_ins._run_plugin(mocked_plg, 'run')

        assert meguca_ins.data['Test'] == 'Test Data'


@mock.patch('meguca.utils.load_config', return_value={'General': {'PluginDirectory': 'Test'}})
@mock.patch('meguca.meguca.Meguca.prepare')
@mock.patch('meguca.plugin.Plugins.load_plugins')
@mock.patch('meguca.plugin.Plugins.get_plugins', return_value=[mock.Mock()])
class TestRunStatPlugins():
    @mock.patch('meguca.meguca.Meguca._run_plugin', return_value=None)
    def test_run_stat_plugins(self, mocked_run_plugin, mocked_get_plugins, mocked_load_plugins,
                              mocked_prepare, mocked_load_config):
        meguca_ins = meguca.Meguca('')

        meguca_ins._run_stat_plugins()

        mocked_run_plugin.assert_called()

    @mock.patch('meguca.meguca.Meguca._run_plugin', side_effect=exceptions.NotFound)
    def test_run_stat_plugins_with_plugin_accesses_non_existent_item_of_param(self, mocked_run_plugin,
                                                                 mocked_get_plugins, mocked_load_plugins,
                                                                 mocked_prepare, mocked_load_config):
        meguca_ins = meguca.Meguca('')

        with pytest.raises(exceptions.NotFound):
            meguca_ins._run_stat_plugins()

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

            meguca_ins._run_stat_plugins()

            assert meguca_ins.data == {'TestData1': 'Test Data', 'TestData2': 'Test Data'}