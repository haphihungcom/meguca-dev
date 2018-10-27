import networkx as nx

from meguca.plugins.src import wa_stats

class TestWAStats():
    def test(self):
        ins = wa_stats.WAStats()
        mocked_data = {'wa_nations': nx.DiGraph([('nation1', 'nation2')]),
                       'regional_nation_num': 2}

        result = ins.run(mocked_data)

        assert result['wa_nation_num'] == 2