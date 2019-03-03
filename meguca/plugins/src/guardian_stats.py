"""Create a list of guardians
"""


import logging

import networkx as nx

from meguca import plugin_categories
from meguca import utils


logger = logging.getLogger(__name__)


class GuardianStats(plugin_categories.Stat):
    def run(self, ns_api):
        required_endorsed = self.plg_config['Criteria']['RequiredToEndorseNations']

        endorsees_list = []
        for nation in required_endorsed:
            endorsees = set(ns_api.get_nation(utils.canonical(nation), 'endorsements')['ENDORSEMENTS'].split(','))
            endorsees_list.append(endorsees)

        guardians = list(set.intersection(*endorsees_list))

        result = {'guardians': guardians}

        logger.debug('Guardian stats generated: %r', result)

        return result
