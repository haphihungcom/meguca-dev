import configparser
from unittest import mock

from meguca.plugins.src import wa_stats


class TestWAStats():
    def test(self):
        ins = wa_stats.WAStats()
        ns_api = mock.Mock(get_wa=mock.Mock(return_value={'NUMNATIONS': '2', 'MEMBERS': 'nation1,nation3'}),
                           get_region=mock.Mock(return_value={'NATIONS': 'nation1:nation2'}))

        config = {'General': {'Region': 'region'}}

        result = ins.run(ns_api=ns_api, config={'Meguca': config})

        assert result == {'region_wa': ['nation1'],
                          'ns_wa_num': 2}
