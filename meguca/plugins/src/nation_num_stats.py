"""Get number of nations in a region and percentages.
"""


import logging

from meguca import plugin_categories


logger = logging.getLogger(__name__)


class NationNumStats(plugin_categories.Stat):
    def run(self, ns_api, config):
        region_nation_num = ns_api.get_region(config['meguca']['general']['region'], 'numnations')['NUMNATIONS']
        ns_nation_num = ns_api.get_world('numnations')['NUMNATIONS']

        result = {'region_nation_num': int(region_nation_num),
                  'ns_nation_num': int(ns_nation_num)}

        logger.debug('Nation number stats generated: %r', result)

        return result
