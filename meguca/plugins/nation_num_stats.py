from meguca import plugin_categories
from meguca.plugins.services.ns_api import ns_api

class NationNumStats(plugin_categories.Stat):
    def run(self, config):
        api = ns_api.NSApi(config['General']['useragent'])

        nation_num = api.get_region(config['General']['region'], 'numnations')['NUMNATIONS']
        ns_nation_num = api.get_world('numnations')['NUMNATIONS']
        nationnum_perc = nation_num / ns_nation_num * 100

        return {'nation_num': nation_num,
                'nation_num_perc': nationnum_perc}