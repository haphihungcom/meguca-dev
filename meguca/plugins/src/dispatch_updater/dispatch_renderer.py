"""Render dispatches from templates.
"""


import jinja2
import bbcode

from meguca.plugins.src.dispatch_updater import filters


FILTERS = {
           'nation': filters.nation,
           'region': filters.region
}


class Renderer():
    """Render dispatches using Jinja and process custom BBcode tags.

    Args:
        template_dir (str): Template file directory.
        bbcode_tags (dict): Custom BBcode tags.
        data (dict): Data.
    """

    def __init__(self, template_dir, bbcode_tags, data):
        template_loader = jinja2.FileSystemLoader(template_dir)

        self.bbcode_parser = bbcode.Parser()
        for tag, info in bbcode_tags.items():
            self.bbcode_parser.add_simple_formatter(tag, info['Template'])

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
        rendered_dispatch = self.bbcode_parser.format(template.render(self.data))

        return rendered_dispatch
