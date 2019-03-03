"""Get total endorsement count and cross-endorsement rate.
"""


import logging

import networkx as nx

from meguca import plugin_categories


logger = logging.getLogger(__name__)


class RegionalEndoStats(plugin_categories.Stat):
    def run(self, data):
        total_endocount = data['wa_nations'].number_of_edges()
        cross_endo = nx.density(data['wa_nations']) * 100

        result = {'total_ec': total_endocount,
                  'cross_endo': cross_endo}

        logger.debug('Regional endorsement stats generated: %r', result)

        return result
