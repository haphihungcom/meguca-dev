"""Render dispatches from templates.
"""


import logging

import jinja2
import bbcode

from meguca.plugins.src.dispatch_updater import filters
from meguca import utils


logger = logging.getLogger(__name__)


FILTERS = {
           'nation': filters.nation,
           'region': filters.region
}


class Renderer():
    """Render dispatches from templates and process custom BBcode tags.

    Args:
        template_dir (str): Template file directory.
        bbcode_tags (dict): Custom BBcode tags.
        data (dict): Data.
    """

    def __init__(self, template_dir, bbcode_tags, custom_vars_dir):
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

        # Context data
        self.ctx = {}

        if isinstance(custom_vars_dir, list):
            for custom_vars_filename in custom_vars_dir:
                self.load_custom_vars(custom_vars_filename)
        else:
            self.load_custom_vars(custom_vars_dir)

    def load_custom_vars(self, custom_vars_filename):
        with open(custom_vars_filename) as f:
            self.ctx.update(utils.load_config(f))
            logger.debug('Loaded custom vars file "%s"', custom_vars_filename)

    def update_data(self, data):
        """Update data for context.

        Args:
            data (dict): General data buss.
        """

        self.ctx.update(data)

    def render_dispatch(self, template_name):
        """Render a dispatch.

        Args:
            template_name (str): Template file name.

        Returns:
            str: Rendered dispatch.
        """

        template = self.env.get_template(template_name)
        rendered_dispatch = self.bbcode_parser.format(template.render(self.ctx))

        logger.debug('Rendered template "%s": %s', template_name, rendered_dispatch)

        return rendered_dispatch
