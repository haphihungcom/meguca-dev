from meguca import plugin_categories


class Test1(plugin_categories.Stat):
    def run(self):
        return {'Madoka': self.plg_config['TestSection']['TestKey']}

    def dry_run(self):
        return {'MadokaDry': self.plg_config['TestSection']['TestKey']}
