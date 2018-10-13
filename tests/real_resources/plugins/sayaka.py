from meguca import plugin_categories

class Test4(plugin_categories.Collector):
    def run(self, config):
        return {'Sayaka': config['Plugin']['Madoka']['TestSection']['TestKey']}

    def prime_run(self, config):
        return {'SayakaPrimeRun': config['Plugin']['Madoka']['TestSection']['TestKey']}