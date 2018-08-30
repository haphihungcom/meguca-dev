import pytest

from meguca import plugin

class TestPlugins():
    def test_load_plugins(self):
        plugins = plugin.Plugins('tests/plugins_for_testing')

        assert plugins.load_plugins()['Test plugin 1']['TestSection']['TestKey'] == 'TestVal'

    def test_get_plugins_by_category(self):
        plugins = plugin.Plugins('tests/plugins_for_testing')
        plugins.load_plugins()

        assert plugins.get_plugins('Stat')[0].name == 'Test plugin 1'


