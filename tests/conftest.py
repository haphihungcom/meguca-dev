import configparser
from unittest import mock

import pytest


@pytest.fixture
def mocked_plg():
    """A mocked plugin with standard entrypoint methods and config.
    It behaves like a real plugin."""
    def stub_run():
        return {'Test': 'Test'}

    def stub_prime_run():
        return {'TestPrime': 'Test Prime'}

    mocked_plg_obj = mock.Mock(run=stub_run, prime_run=stub_prime_run)
    config = configparser.ConfigParser()
    config['Core'] = {'ConfigFile': 'Test'}
    config['Scheduling'] = {'ScheduleMode': 'interval',
                            'seconds': '1'}
    mocked_plg = mock.Mock(plugin_object=mocked_plg_obj,
                           details=config)
    type(mocked_plg).name = mock.PropertyMock(return_value='Test')

    return mocked_plg