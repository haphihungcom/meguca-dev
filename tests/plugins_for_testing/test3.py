from meguca import plugin_categories

class Test3(plugin_categories.Collector):
    def run(self):
        return {'TestKey3': 'TestVal3'}

    def prime_run(self):
        return {'TestKey3': 'TestVal3'}