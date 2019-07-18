from meguca import plugin_categories

class Test4(plugin_categories.Collector):
    def run(self, config):
        return {'Sayaka': config['plugins']['Madoka']['TestSection']['TestKey']}

    def prepare(self, nagisa):
        return {'SayakaPrep': nagisa}

    def dry_run(self, nagisa):
        return {'SayakaDry': nagisa}
