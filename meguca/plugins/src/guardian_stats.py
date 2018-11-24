import networkx as nx

from meguca import plugin_categories
from meguca import utils


class GuardianStats(plugin_categories.Stat):
    def run(self, ns_api):
        required_endorsed = utils.canonical(self.plg_config['Criteria']['requiredendorsednations']).split(',')

        endorsees_list = []
        for nation in required_endorsed:
            endorsees = set(ns_api.get_nation(nation, 'endorsements')['ENDORSEMENTS'].split(','))
            endorsees_list.append(endorsees)

        guardians = list(set.intersection(*endorsees_list))

        return {'guardians': guardians}
