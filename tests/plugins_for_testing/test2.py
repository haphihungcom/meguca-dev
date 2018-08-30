from meguca import plugin_categories

class Test2(plugin_categories.Stat):
    def run(self, data):
        return {'TestKey2': data['TestKey4']}