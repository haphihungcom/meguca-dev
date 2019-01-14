import configparser
from unittest import mock

import pytest


@pytest.fixture
def mock_plg():
    """A mock plugin with standard entry methods and config.
    It behaves like a real plugin."""

    def stub_run():
        return {'Test': 'Test'}

    def stub_prime_run():
        return {'TestPrime': 'Test Prime'}

    mock_plg_obj = mock.Mock(run=stub_run, prime_run=stub_prime_run)
    config = configparser.ConfigParser()
    config['Core'] = {'ConfigFile': 'Test'}
    config['Scheduling'] = {'ScheduleMode': 'interval',
                            'seconds': '1'}
    mock_plg = mock.Mock(plugin_object=mock_plg_obj,
                         details=config)
    type(mock_plg).name = mock.PropertyMock(return_value='Test')

    return mock_plg