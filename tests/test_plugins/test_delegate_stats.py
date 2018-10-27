import configparser
from unittest import mock

from meguca.plugins.src import delegate_stats

class TestDelegateStats():
    def test(self):
        ins = delegate_stats.DelegateStats()
        mocked_plg_config = configparser.ConfigParser()
        mocked_plg_config['Delegate'] = {'name': 'fudgetopia'}
        ins.plg_config = mocked_plg_config
        mocked_nsapi = mock.Mock(get_nation=mock.Mock(return_value={'CENSUS': {'SCALE': {'SCORE': '1'}}}),
                                 get_region=mock.Mock(return_value={'DELEGATE': 'fudgetopia'}))

        mocked_config = {'Meguca': configparser.ConfigParser()}
        mocked_config['Meguca']['General'] = {'useragent': '', 'region': 'region'}

        result = ins.run(ns_api=mocked_nsapi, config=mocked_config)

        result == {'incumbent_delegate': 'fudgetopia',
                   'delegate_ec': 1}