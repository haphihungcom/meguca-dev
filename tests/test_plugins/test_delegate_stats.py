import configparser
from unittest import mock

from meguca.plugins.src import delegate_stats


class TestDelegateStats():
    def test(self):
        ins = delegate_stats.DelegateStats()
        plg_config = configparser.ConfigParser()
        plg_config['Delegate'] = {'name': 'fudgetopia'}
        ins.plg_config = plg_config
        ns_api = mock.Mock(get_nation=mock.Mock(return_value={'CENSUS': {'SCALE': {'SCORE': '1'}}}),
                          get_region=mock.Mock(return_value={'DELEGATE': 'fudgetopia'}))

        config = {'Meguca': configparser.ConfigParser()}
        config['Meguca']['General'] = {'useragent': '', 'region': 'region'}

        result = ins.run(ns_api=ns_api, config=config)

        result == {'incumbent_delegate': 'fudgetopia',
                   'delegate_ec': 1}