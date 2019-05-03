"""Render dispatches from templates.
"""

import importlib
import logging
import inspect

import toml
import jinja2
import bbcode

from meguca import utils
from meguca.plugins.src.dispatch_updater import utils as dispatch_utils


logger = logging.getLogger(__name__)


class CustomVars():
    """Custom variables.

        Args:
            custom_vars_files (str|list): Custom vars files.
    """

    def __init__(self, custom_vars_files):
        self._custom_vars = {}

        if isinstance(custom_vars_files, list):
            for custom_vars_file in custom_vars_files:
                self.load_custom_vars(custom_vars_file)
        elif custom_vars_files == '':
            self._custom_vars = {}
        else:
            self.load_custom_vars(custom_vars_files)

    def load_custom_vars(self, custom_vars_file):
            self._custom_vars.update(utils.load_config(custom_vars_file))
            logger.debug('Loaded custom vars file "%s"', custom_vars_file)

    @property
    def custom_vars(self):
        return self._custom_vars


class BBParser():
    """Parse BBCode tags.

       Args:
            simple_bb_path (str): Path to simple BBCode formatter file.
            bb_path (str): Path to BBCode formatter file.
            custom_vars (dict): Custom variables to pass to formatters.
            config (dict): Plugin configuration to pass to formatters.
    """

    def __init__(self, simple_bb_path, bb_path, custom_vars, config):
        self.parser = bbcode.Parser(newline='\n',
                                    install_defaults=False,
                                    escape_html=False)
        self.custom_vars = custom_vars
        self.config = config

        try:
            for tag, info in toml.load(simple_bb_path).items():
                self.parser.add_simple_formatter(tag, info['template'], render_embedded=True)
                logger.debug('Loaded simple BBCode formatter "%s"', tag)
        except FileNotFoundError:
            logger.warning('Simple BBCode formatter file not found!')

        formatters = dispatch_utils.load_funcs(bb_path)
        if formatters is None:
            logger.warning('BBCode formatter file not found!')
        else:
            for formatter in formatters:
                self.parser.add_formatter(formatter[0],formatter[1],
                                          render_embedded=True,
                                          swallow_trailing_newline=True)
                logger.debug('Loaded BBCode formatter "%s"', formatter[0])
            logger.info('Loaded all BBCode formatters')

    def format(self, text):
        return self.parser.format(text, config=self.config,
                                  custom_vars=self.custom_vars)


class TemplateRenderer():
    def __init__(self, template_dir, filters_path):
        template_loader = jinja2.FileSystemLoader(template_dir)
        self.env = jinja2.Environment(loader=template_loader)

        filters = dispatch_utils.load_funcs(filters_path)
        if filters is None:
            logger.warning('Filter file not found!')
        else:
            loaded_filters = {}
            for filter in filters:
                loaded_filters[filter[0]] = filter[1]
                logger.debug('Loaded filter "%s"', filter[0])
            self.env.filters.update(loaded_filters)
            logger.info('Loaded all custom filters')

    def render(self, template_name, context):
        """Render a dispatch template.

        Args:
            template_name (str): Template name.
            context (dict): Context for the template.

        Returns:
            str: Rendered template.
        """

        return self.env.get_template(template_name).render(context)


class Renderer():
    """Render dispatches from templates and process custom BBcode tags.

    Args:
        template_dir (str): Template file directory.
        filter_path (str): Path to template filter file.
        simple_bb_path (str): Path to simple BBCode formatter file.
        bb_path (str): Path to BBCode formatter file.
        data (dict): Data.
        custom_vars_files (list|str): Custom vars files.
        plg_config: Plugin configuration.
    """

    def __init__(self, template_dir, filter_path, simple_bb_path,
                 bb_path, custom_vars_files, plg_config):
        custom_vars = CustomVars(custom_vars_files)
        self.template_renderer = TemplateRenderer(template_dir, filter_path)
        self.bb_parser = BBParser(simple_bb_path, bb_path,
                                  custom_vars.custom_vars, plg_config)

        # Context for templates
        self.ctx = custom_vars.custom_vars

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

        rendered = self.template_renderer.render(template_name, self.ctx)
        rendered = self.bb_parser.format(rendered)

        logger.debug('Rendered template "%s": %s', template_name, rendered)

        return rendered
