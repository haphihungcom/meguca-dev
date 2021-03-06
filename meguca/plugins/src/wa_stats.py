"""Get WA nation number and percentages
"""


import logging

from meguca import plugin_categories


logger = logging.getLogger(__name__)


class WAStats(plugin_categories.Stat):
    def run(self, ns_api, config):
        wa_data = ns_api.get_wa('ga', ['numnations', 'members'])

        ns_wa_num = int(wa_data['NUMNATIONS'])

        region_nations = set(ns_api.get_region(config['meguca']['general']['region'],
                                               'nations')['NATIONS'].split(':'))
        ns_wa_nations = set(wa_data['MEMBERS'].split(','))
        region_wa_nations = list(region_nations & ns_wa_nations)

        result = {'region_wa': region_wa_nations,
                  'ns_wa_num': ns_wa_num}

        logger.debug('WA nation number stats generated: %r', result)

        return result
