"""Render dispatches from templates.
"""


import logging

import jinja2
import bbcode

from meguca.plugins.src.dispatch_updater import filters


logger = logging.getLogger(__name__)


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

    def __init__(self, template_dir, bbcode_tags):
        template_loader = jinja2.FileSystemLoader(template_dir)

        self.bbcode_parser = bbcode.Parser(newline='\n',
                                           install_defaults=False,
                                           escape_html=False)
        for tag, info in bbcode_tags.items():
            self.bbcode_parser.add_simple_formatter(tag, info['template'])
            logger.debug('Loaded custom BBCode tag "%s"', tag)
        logger.info('Loaded all custom BBCode tags')

        self.env = jinja2.Environment(loader=template_loader)
        self.env.filters.update(FILTERS)
        logger.info('Loaded all custom filters')

        self.data = None

    def render_dispatch(self, template_name):
        """Render a dispatch.

        Args:
            template_name (str): Template file name.

        Returns:
            str: Rendered dispatch.
        """

        template = self.env.get_template(template_name)
        rendered_dispatch = self.bbcode_parser.format(template.render(self.data))

        logger.debug('Rendered template "%s": %s', template_name, rendered_dispatch)

        return rendered_dispatch
