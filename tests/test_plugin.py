from unittest import mock

import pytest

from meguca import plugin
from meguca import exceptions


@mock.patch('meguca.utils.load_config', return_value='Test')
@mock.patch('yapsy.PluginManager.PluginManager.collectPlugins')
@mock.patch('yapsy.PluginManager.PluginManager.activatePluginByName')
class TestPlugins():
    @pytest.mark.usefixtures('mock_plg')
    def test_load_plugins_with_existing_plugins(self, activatePluginByName, collectPlugins,
                                                load_config, mock_plg):
        with mock.patch('yapsy.PluginManager.PluginManager.getAllPlugins') as getAllPlugins:
            getAllPlugins.return_value = [mock_plg()]

            plugins_ins = plugin.Plugins('','')

            assert plugins_ins.load_plugins() == {'Test': 'Test'}

    def test_load_plugins_with_no_plugins_found(self, activatePluginByName, collectPlugins,
                                                load_config, mock_plg):
        with mock.patch('yapsy.PluginManager.PluginManager.getAllPlugins') as getAllPlugins:
            getAllPlugins.return_value = []

            plugins_ins = plugin.Plugins('','')

            with pytest.raises(exceptions.PluginError):
                plugins_ins.load_plugins()

    def test_load_plugins_with_plugin_not_have_id(self, activatePluginByName, collectPlugins,
                                                  load_config, mock_plg):
        with mock.patch('yapsy.PluginManager.PluginManager.getAllPlugins') as getAllPlugins:
            mock_plg = mock_plg()
            mock_plg.details['Core'].pop('Id')
            getAllPlugins.return_value = [mock_plg]

            plugins_ins = plugin.Plugins('','')

            with pytest.raises(exceptions.PluginError):
                plugins_ins.load_plugins()

    @mock.patch('yapsy.PluginManager.PluginManager.getPluginsOfCategory', return_value='Test')
    def test_get_plugins_with_existing_plugins(self, getPluginsOfCategory, activatePluginByName,
                                               collectPlugins, load_config):
        plugins_ins = plugin.Plugins('','')

        assert plugins_ins.get_plugins('Test') == 'Test'
    @mock.patch('yapsy.PluginManager.PluginManager.getPluginsOfCategory', return_value=[])
    def test_get_plugins_with_no_plugins(self, getPluginsOfCategory, activatePluginByName,
                                         collectPlugins, load_config):
        plugins_ins = plugin.Plugins('','')

        assert plugins_ins.get_plugins('Test') == None
    @mock.patch('yapsy.PluginManager.PluginManager.getAllPlugins', return_value='Test')
    def test_get_all_plugins(self, getAllPlugins, activatePluginByName,
                             collectPlugins, load_config):
        plugins_ins = plugin.Plugins('','')

        assert plugins_ins.get_all_plugins() == 'Test'
