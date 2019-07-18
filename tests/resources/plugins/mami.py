from meguca import plugin_categories

class Test5(plugin_categories.View):
    def run(self, data):
        print('Hello World! %s', data['Madoka'])

    def prepare(self, nagisa):
        print(nagisa)
