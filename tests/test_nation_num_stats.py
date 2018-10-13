import configparser
from unittest import mock

import networkx as nx

from meguca.plugins import nation_num_stats

class TestRegionalEndoStats():
    @mock.patch('meguca.plugins.services.ns_api.ns_api.NSApi.get_world', return_value={'NUMNATIONS': 4})
    @mock.patch('meguca.plugins.services.ns_api.ns_api.NSApi.get_region', return_value={'NUMNATIONS': 2})
    def test(self, mocked_get_region, mocked_get_world):
        ins = nation_num_stats.NationNumStats()
        mocked_config = configparser.ConfigParser()
        mocked_config['General'] = {'useragent': '', 'region': 'region'}

        result = ins.run(mocked_config)

        assert result['nation_num'] == 2
        assert result['nation_num_perc'] == 50