from .. import plugin_api as pa

class WAStats(plugin_category.Stats):
    def run():
        wa_nation_num = pa.data['wa_nations'].number_of_nodes()
        wa_nation_perc = wa_nation_num / pa.data['regional_nation_num'] * 100

        return {'wa_nation_num': wa_nation_num,
                'wa_nation_perc': wa_nation_perc}