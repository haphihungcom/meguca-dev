from meguca import plugin_categories

class NationNumStats(plugin_categories.Stat):
    def run(self, ns_api, config):
        nation_num = ns_api.get_region(config['Meguca']['General']['region'], 'numnations')['NUMNATIONS']
        ns_nation_num = ns_api.get_world('numnations')['NUMNATIONS']

        return {'nation_num': nation_num}