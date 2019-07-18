"""Render dispatches from templates.
"""


import importlib
import logging
import inspect

import toml
import jinja2
import bbcode

from meguca import utils
from meguca.plugins.src.dispatch_updater import utils as plg_utils
from meguca.plugins.src.dispatch_updater import exceptions


logger = logging.getLogger(__name__)


class CustomVars():
    """Custom variables.

        Args:
            custom_vars_path (str|list): Custom vars files.
    """

    def __init__(self, custom_vars_path):
        self._custom_vars = {}

        if isinstance(custom_vars_path, list):
            for custom_vars_file in custom_vars_path:
                self.load_custom_vars(custom_vars_file)
        elif custom_vars_path == '':
            pass
        else:
            self.load_custom_vars(custom_vars_path)

    def load_custom_vars(self, custom_vars_file):
            self._custom_vars.update(utils.load_config(custom_vars_file))
            logger.debug('Loaded custom vars file "%s"', custom_vars_file)

    @property
    def custom_vars(self):
        return self._custom_vars


class BBParser():
    """Parse BBCode tags.

       Args:
            bb_config (dict): BBCode formatter configurations.
            custom_vars (dict): Custom variables to pass to formatters.
            ext_config (dict): Plugin configuration to pass to formatters.
    """

    def __init__(self, bb_config, custom_vars, ext_config):
        self.parser = bbcode.Parser(newline='\n',
                                    install_defaults=False,
                                    escape_html=False,
                                    replace_links=False,
                                    replace_cosmetic=False)

        self.custom_vars = custom_vars
        self.ext_config = ext_config

        for tag, info in bb_config['simple_formatters'].items():
            self.parser.add_simple_formatter(tag, info['template'],
                                             escape_html=False,
                                             replace_links=False,
                                             replace_cosmetic=False,
                                             newline_closes=info['newline_closes'],
                                             same_tag_closes=info['same_tag_closes'],
                                             standalone=info['standalone'],
                                             render_embedded=info['render_embedded'],
                                             strip=info['strip'],
                                             swallow_trailing_newline=info['swallow_trailing_newline'])
            logger.debug('Loaded simple BBCode formatter "%s" | "%s"', tag, info)

        for tag, info in bb_config['formatters'].items():
            try:
                funcs = plg_utils.load_funcs(info['func_path'])
            except FileNotFoundError:
                raise exceptions.BBParserError("Couldn't find BBCode formatter function file %s",
                                               info['func_path'])
            if funcs is None:
                raise exceptions.BBParserError("Couldn't find any function in %s",
                                               info['func_path'])

            format_func = None
            for func in funcs:
                if func[0] == info['func_name']:
                    format_func = func[1]
            if format_func is None:
                raise exceptions.BBParserError('Format function %s did not found in %s',
                                               info['func_name'], info['func_path'])

            self.parser.add_formatter(tag, format_func,
                                      escape_html=False,
                                      replace_links=False,
                                      replace_cosmetic=False,
                                      newline_closes=info['newline_closes'],
                                      same_tag_closes=info['same_tag_closes'],
                                      standalone=info['standalone'],
                                      render_embedded=info['render_embedded'],
                                      strip=info['strip'],
                                      swallow_trailing_newline=info['swallow_trailing_newline'])
            logger.debug('Loaded BBCode formatter "%s" | "%s"', tag, info)

        logger.info('Loaded all BBCode formatters')

    def format(self, text):
        return self.parser.format(text, config=self.ext_config,
                                  custom_vars=self.custom_vars)


class TemplateRenderer():
    def __init__(self, template_dir_path, filters_path):
        """Render a dispatch template.

        Args:
            template_dir_path (str): Template file directory.
            filters_path (str): Path to filters file.
        """
        template_loader = jinja2.FileSystemLoader(template_dir_path)
        self.env = jinja2.Environment(loader=template_loader, trim_blocks=True)

        filters = plg_utils.load_funcs(filters_path)
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
        template_dir_path (str): Template file directory.
        filters_path (str): Path to filters file.
        bb_path (str): Path to BBCode formatter configuration file.
        data (dict): Data.
        custom_vars_files (list|str): Custom vars files.
        plg_config: Plugin configuration.
    """

    def __init__(self, template_dir_path, filters_path,
                 bb_path, custom_vars_path, plg_config):
        custom_vars = CustomVars(custom_vars_path)
        self.template_renderer = TemplateRenderer(template_dir_path, filters_path)

        try:
            bb_config = utils.load_config(bb_path)
            self.bb_parser = BBParser(bb_config, custom_vars.custom_vars, plg_config)
        except FileNotFoundError:
            raise exceptions.BBParserError('BBCode configuration file not found!')

        # Context for templates
        self.ctx = custom_vars.custom_vars

    def update_data(self, data):
        """Update context with new data.

        Args:
            data (dict): New data.
        """

        self.ctx.update(data)

    def render(self, template_path, dispatch_name):
        """Render a dispatch.

        Args:
            template_path (str): Template file path.
            dispatch_name (str): Current dispatch name.

        Returns:
            str: Rendered dispatch.
        """

        render_ctx = self.ctx
        render_ctx['current_dispatch'] = dispatch_name

        rendered = self.template_renderer.render(template_path, render_ctx)
        rendered = self.bb_parser.format(rendered)

        logger.debug('Rendered template "%s"', template_path)

        return rendered
