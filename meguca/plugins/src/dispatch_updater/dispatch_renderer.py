"""Render dispatches from templates.
"""


import jinja2

from meguca.plugins.src.dispatch_updater import filters


FILTERS = {
           'nation': filters.nation,
           'region': filters.region
}


class Renderer():
    """Render dispatches using Jinja.

    Args:
        template_dir (str): Template file directory.
        data (dict): Data.
    """

    def __init__(self, template_dir, data):
        template_loader = jinja2.FileSystemLoader(template_dir)
        self.env = jinja2.Environment(loader=template_loader)
        self.env.filters.update(FILTERS)

        self.data = data

    def render_dispatch(self, template_name):
        """Render a dispatch.

        Args:
            template_name (str): Template file name.

        Returns:
            str: Rendered dispatch.
        """

        template = self.env.get_template(template_name)
        return template.render(self.data)
