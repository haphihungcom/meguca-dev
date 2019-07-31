"""Render dispatches from templates.
"""

import logging

import toml
import jinja2
import bbcode

from meguca.plugins.src.dispatch_updater import bb_parser
from meguca.plugins.src.dispatch_updater import utils


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
            logger.debug('No custom vars file found')
        else:
            self.load_custom_vars(custom_vars_path)

    def load_custom_vars(self, custom_vars_file):
        """Load custom vars from files

        Args:
            custom_vars_file (str): Custom vars file name
        """

        try:
            self._custom_vars.update(toml.load(custom_vars_file))
            logger.debug('Loaded custom vars file "%s"', custom_vars_file)
        except FileNotFoundError:
            raise FileNotFoundError('Custom vars file "%s" not found'.format(custom_vars_file))

    @property
    def custom_vars(self):
        return self._custom_vars


class TemplateRenderer():
    """Render a dispatch template.

        Args:
            template_dir_path (str): Template file directory.
            filters_path (str): Path to filters file.
            template_ext (str): Template file extension.
    """

    def __init__(self, template_dir_path, filters_path, template_ext):
        template_loader = jinja2.FileSystemLoader(template_dir_path)
        # Make access to undefined context variables generate logs.
        undef = jinja2.make_logging_undefined(logger=logger)
        self.env = jinja2.Environment(loader=template_loader, trim_blocks=True, undefined=undef)
        self.template_ext = template_ext

        if filters_path is not None:
            filters = utils.get_funcs(filters_path)
            if filters is None:
                logger.warning('Filter file not found!')
            else:
                loaded_filters = {}
                for filter in filters:
                    loaded_filters[filter[0]] = filter[1]
                    logger.debug('Loaded filter "%s"', filter[0])
                self.env.filters.update(loaded_filters)
                logger.info('Loaded all custom filters')

    def validate_templates(self):
        """Validate syntax and existence of templates.
        """

        for template in self.env.list_templates(extensions=self.template_ext):
            try:
                self.env.get_template(template)
            except jinja2.TemplateSyntaxError as e:
                logger.error('Dispatch template "%s" syntax error at line %d: %s',
                             template, e.lineno, e.message)

    def render(self, name, context):
        """Render a dispatch template.

        Args:
            name (str): Dispatch template name.
            context (dict): Context for the template.

        Returns:
            str: Rendered template.
        """

        template_path = '{}.{}'.format(name, self.template_ext)
        return self.env.get_template(template_path).render(context)


class Renderer():
    """Render dispatches from templates and process custom BBcode tags.

    Args:
        config: Configuration.
    """

    def __init__(self, config):
        template_config = config.get('template', None)
        if template_config is None or 'template_dir_path' not in template_config:
            logger.error('Dispatch template path not configured!')
        else:
            self.template_renderer = TemplateRenderer(template_config.get('template_dir_path', None),
                                                      template_config.get('filters_path', None),
                                                      template_config.get('template_file_ext', None))

        bb_config = config.get('bbcode', None)
        if bb_config is None:
            self.bb_parser = None
            logger.warning('BBCode parser not configured!')
        else:
            self.bb_parser = bb_parser.BBParser(bb_config.get('simple_formatter_path', None),
                                                bb_config.get('complex_formatter_path', None),
                                                bb_config.get('complex_formatter_config_path', None))

        custom_vars = CustomVars(config.pop('custom_vars_path', None))

        # Context for templates
        self.ctx = custom_vars.custom_vars

    def update_ctx(self, data, plg_config, config, dispatch_info):
        """Update context with new info.

        Args:
            data (dict): New data.
            plg_config (dict): Our plugin's configuration.
            config (dict): Meguca and other plugins' configuration.
            dispatch_info (dict): Dispatch information.
        """

        self.ctx.update({'data_products': data, 'config': plg_config,
                         'ext_config': config, 'dispatch_info': dispatch_info})

    def render(self, name):
        """Render a dispatch.

        Args:
            name (str): Dispatch file name.

        Returns:
            str: Rendered dispatch.
        """

        self.ctx['current_dispatch'] = {'name': name}
        self.ctx['current_dispatch'].update(self.ctx['dispatch_info'][name])

        rendered = self.template_renderer.render(name, self.ctx)
        if self.bb_parser is not None:
            rendered = self.bb_parser.format(rendered, **self.ctx)

        logger.debug('Rendered dispatch "%s"', name)

        return rendered
