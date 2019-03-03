from unittest import mock

import pytest

from meguca import plugin
from meguca import exceptions


@mock.patch('meguca.utils.load_config', return_value='Test')
@mock.patch('yapsy.PluginManager.PluginManager.collectPlugins')
@mock.patch('yapsy.PluginManager.PluginManager.activatePluginByName')
class TestPlugins():
    @pytest.mark.usefixtures('mock_plg')
    def test_load_plugins(self, activatePluginByName, collectPlugins,
                          load_config, mock_plg):
        with mock.patch('yapsy.PluginManager.PluginManager.getAllPlugins') as getAllPlugins:
            getAllPlugins.return_value = [mock_plg]

            plugins_ins = plugin.Plugins('','')

            assert plugins_ins.load_plugins() == {'Test': 'Test'}

    @mock.patch('yapsy.PluginManager.PluginManager.getPluginsOfCategory', return_value='Test')
    def test_get_plugins(self, getPluginsOfCategory, activatePluginByName,
                         collectPlugins, load_config):
        plugins_ins = plugin.Plugins('','')

        assert plugins_ins.get_plugins('Test') == 'Test'


class TestEntryParam():
    def test_getitem(self):
        param = plugin.EntryParam({'Test': 'Test'})

        assert param['Test'] == 'Test'

    def test_getitem_on_non_existent_item(self):
        param = plugin.EntryParam({'Test': 'Test'})

        with pytest.raises(exceptions.NotFound):
            param['Test1']

    def test_getitem_on_non_existent_item_with_raise_notyetexist_on(self):
        param = plugin.EntryParam({'Test': 'Test'}, raise_notyetexist=True)

        with pytest.raises(exceptions.NotYetExist):
            param['Test1']
