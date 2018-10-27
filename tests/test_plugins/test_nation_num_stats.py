import configparser
from unittest import mock

from meguca.plugins.src import nation_num_stats

class TestNationNumStats():
    def test(self):
        ins = nation_num_stats.NationNumStats()
        mocked_nsapi = mock.Mock(get_world=mock.Mock(return_value={'NUMNATIONS': '4'}),
                                 get_region=mock.Mock(return_value={'NUMNATIONS': '2'}))
        mocked_config = {'Meguca': configparser.ConfigParser()}
        mocked_config['Meguca']['General'] = {'useragent': '', 'region': 'region'}

        result = ins.run(ns_api=mocked_nsapi, config=mocked_config)

        assert result == {'region_nation_num': 2,
                          'ns_nation_num': 4}