from .. import plugin_category

class WAStats(plugin_category.Stats):
    def run(self, data):
        wa_nation_num = data['wa_nations'].number_of_nodes()
        wa_nation_perc = wa_nation_num / data['regional_nation_num'] * 100

        return {'wa_nation_num': wa_nation_num,
                'wa_nation_perc': wa_nation_perc}