from meguca import plugin_categories

class Test3(plugin_categories.Stat):
    def run(self, config):
        return {'TestKey4': config['Plugin']['Test plugin 1']['TestSection']['TestKey']}