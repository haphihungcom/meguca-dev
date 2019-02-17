import networkx as nx

from meguca.plugins.src import regional_endo_stats

class TestRegionalEndoStats():
    def test(self):
        ins = regional_endo_stats.RegionalEndoStats()
        data = {'wa_nations': nx.DiGraph([('nation1', 'nation2'), ('nation2', 'nation1')])}

        result = ins.run(data)

        assert result['total_ec'] == 2
        assert result['cross_endo'] == 100
