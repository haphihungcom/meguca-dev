import jinja2

from meguca import plugin_categories


class TemplateProcessor():
    def __init__(self, template_dir, data):
        template_loader = jinja2.FileSystemLoader(template_dir)
        self.jinja_env = jinja2.Environment(loader=template_loader)
        self.data = data

    def process_template(self, template_name):
        template = self.jinja_env.get_template(template_name)
        return template.render(self.data)


class DispatchUpdater(plugin_categories.View):
    def run(self, data, ns_site):
        template_processor = TemplateProcessor(self.plg_config['General']['TemplateDirectory'], data)
        self.ns_site = ns_site

        templates = self.plg_config['Dispatches']
        for template_name, template_info in templates.items():
            content = template_processor.process_template(template_name)
            self.update_dispatch(template_info, content)

    def update_dispatch(self, template_info, content):
        subcategory_name = "subcategory-{}".format(template_info['Category'])
        params = {'edit': str(template_info['Id']),
                  'category': str(template_info['Category']),
                  subcategory_name: str(template_info['Subcategory']),
                  'dname': template_info['Title'],
                  'message': content,
                  'submitbutton': '1'}

        self.ns_site.execute('lodge_dispatch', params)