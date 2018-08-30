from meguca import plugin_categories

class Test1(plugin_categories.Stat):
    def run(self):
        return {'TestKey1': self.plg_config['TestSection']['TestKey']}