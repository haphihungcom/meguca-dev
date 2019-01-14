from meguca import plugin_categories


class NationNumStats(plugin_categories.Stat):
    def run(self, ns_api, config):
        region_nation_num = ns_api.get_region(config['Meguca']['General']['Region'], 'numnations')['NUMNATIONS']
        ns_nation_num = ns_api.get_world('numnations')['NUMNATIONS']

        return {'region_nation_num': int(region_nation_num),
                'ns_nation_num': int(ns_nation_num)}