import configparser
from unittest import mock

from meguca.plugins.src import wa_stats


class TestWAStats():
    def test(self):
        ins = wa_stats.WAStats()
        mocked_nsapi = mock.Mock(get_wa=mock.Mock(return_value={'NUMNATIONS': '2', 'MEMBERS': 'nation1,nation3'}),
                                 get_region=mock.Mock(return_value={'NATIONS': 'nation1:nation2'}))
        mocked_config = {'Meguca': configparser.ConfigParser()}
        mocked_config['Meguca']['General'] = {'useragent': '', 'region': 'region'}

        result = ins.run(ns_api=mocked_nsapi, config=mocked_config)

        result == {'region_wa_num': 1,
                   'ns_wa_num': 2}