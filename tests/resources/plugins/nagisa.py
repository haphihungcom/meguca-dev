from meguca import plugin_categories

class Nagisa(plugin_categories.Service):
    def get(self):
        return 'TestVal'