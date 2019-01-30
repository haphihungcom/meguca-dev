"""Create dispatches based on templates and upload them.
"""


import jinja2

from meguca import plugin_categories


class DispatchRenderer():
    """Render dispatches using Jinja.

    Args:
        template_dir (str): Template file directory.
        data (dict): Data.
    """

    def __init__(self, template_dir, data):
        template_loader = jinja2.FileSystemLoader(template_dir)
        self.jinja_env = jinja2.Environment(loader=template_loader)
        self.data = data

    def render_dispatch(self, template_name):
        """Render a dispatch.

        Args:
            template_name (str): Template file name.

        Returns:
            str: Rendered dispatch.
        """

        template = self.jinja_env.get_template(template_name)
        return template.render(self.data)


class DispatchUpdater(plugin_categories.View):
    def run(self, data, ns_site):
        dispatch_renderer = DispatchRenderer(self.plg_config['General']['TemplateDirectory'], data)
        self.ns_site = ns_site

        dispatches = self.plg_config['Dispatches']
        for name, info in dispatches.items():
            content = dispatch_renderer.render_dispatch(name)
            self.update_dispatch(info, content)

    def update_dispatch(self, dispatch_info, content):
        """Update dispatch.

        Args:
            dispatch_info (dict): Dispatch information.
            content (str): New content.
        """

        subcategory_name = "subcategory-{}".format(dispatch_info['Category'])
        params = {'edit': str(dispatch_info['Id']),
                  'category': str(dispatch_info['Category']),
                  subcategory_name: str(dispatch_info['Subcategory']),
                  'dname': dispatch_info['Title'],
                  'message': content,
                  'submitbutton': '1'}

        self.ns_site.execute('lodge_dispatch', params)