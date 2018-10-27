from meguca import plugin_categories


class WAStats(plugin_categories.Stat):
    def run(self, ns_api, config):
        wa_data = ns_api.get_wa('ga', ['numnations', 'members'])

        ns_wa_num = wa_data['NUMNATIONS']

        region_nations = set(ns_api.get_region(config['Meguca']['General']['region'],
                                               'nations')['NATIONS'].split(':'))
        ns_wa_nations = set(wa_data['MEMBERS'].split(','))
        region_wa_num = len(region_nations & ns_wa_nations)

        return {'region_wa_num': region_wa_num,
                'ns_wa_num': int(ns_wa_num)}