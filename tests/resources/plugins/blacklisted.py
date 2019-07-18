from meguca import plugin_categories

class Blacklisted(plugin_categories.Collector):
    def run(self):
        return {'TestBlack': 'TestVal'}
