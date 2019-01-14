import networkx as nx

from meguca import plugin_categories
from meguca import utils


class GuardianStats(plugin_categories.Stat):
    def run(self, ns_api):
        required_endorsed = self.plg_config['Criteria']['RequiredToEndorseNations']

        endorsees_list = []
        for nation in required_endorsed:
            endorsees = set(ns_api.get_nation(utils.canonical(nation), 'endorsements')['ENDORSEMENTS'].split(','))
            endorsees_list.append(endorsees)

        guardians = list(set.intersection(*endorsees_list))

        return {'guardians': guardians}
