"""Parse BBCode tags.
"""

import copy
import logging

import toml
import bbcode

from meguca import utils
from meguca.plugins.src.dispatch_updater import utils as bb_utils


logger = logging.getLogger(__name__)


class BBRegistry():
    """Complex formatter registry.
    """

    complex_formatters = []

    @classmethod
    def register(cls, tag_name, **kwargs):
        """[summary]

        Args:
            tag_name (str): Tag name.
        """

        def decorator(class_obj):
            kwargs['obj'] = class_obj()
            kwargs['tag_name'] = tag_name
            cls.complex_formatters.append(kwargs)

        return decorator

    @classmethod
    def init_complex_formatters(cls, path, config):
        """Initialize complex formatters and give them config.

        Args:
            path (str): Path to complex formatter file.
            config (dict): Complex formatter config.
        """

        try:
            bb_utils.load_classes(path)
            logger.debug('Loaded complex formatter file at "{}"'.format(path))
        except FileNotFoundError:
            raise FileNotFoundError('Could not find complex formatter file at "{}"'.format(path))

        for formatter in cls.complex_formatters:
            tag_name = formatter['tag_name']
            if tag_name in config:
                formatter['obj'].config = config[tag_name]
                logger.debug('Loaded complex formatter "%s" configuration: %r', tag_name, config[tag_name])


class BBParserCore():
    """Parse BBCode tags.

       Args:
            bb_config (dict): BBCode formatter configuration.
            custom_vars (dict): Custom variables to pass to formatters.
    """

    def __init__(self):
        self.parser = bbcode.Parser(newline='\n',
                                    install_defaults=False,
                                    escape_html=False,
                                    replace_links=False,
                                    replace_cosmetic=False)

    def add_simple_formatter(self, tag_name, template, **kwargs):
        """Add a simple formatter.

        Args:
            tag_name (str): Tag name.
            format_string (func): Template.
        """

        self.parser.add_simple_formatter(tag_name=tag_name,
                                         format_string=template,
                                         **kwargs)

    def add_complex_formatter(self, tag_name, render_func, **kwargs):
        """Add a complex formatter.

        Args:
            tag_name (str): Tag name.
            render_func (func): Render function.
        """

        self.parser.add_formatter(tag_name=tag_name,
                                  render_func=render_func,
                                  **kwargs)

    def format(self, text, **kwargs):
        return self.parser.format(text, **kwargs)


class BBParserLoader():
    def __init__(self, parser, bb_registry, config):
        self.parser = parser
        self.simple_formatter_path = config.get('simple_formatter_path', None)
        self.complex_formatter_path = config.get('complex_formatter_path', None)
        self.complex_formatter_config_path = config.get('complex_formatter_config_path', None)
        self.bb_registry = bb_registry

    def load_parser(self):
        self.load_simple_formatters()
        self.load_complex_formatters()
        logger.info('Loaded all BBCode formatters')

        return self.parser

    def load_simple_formatters(self):
        if self.simple_formatter_path is None:
            return

        try:
            simple_formatters = toml.load(self.simple_formatter_path)
        except FileNotFoundError:
            logger.error('Simple formatter file not found at "%s"', self.simple_formatter_path)
            return

        for tag_name, conf in simple_formatters.items():
            if 'template' not in conf:
                logger.error('"%s" does not have a template.', tag_name)
                continue

            self.parser.add_simple_formatter(
                tag_name=tag_name,
                template=conf['template'],
                escape_html=False,
                replace_links=False,
                replace_cosmetic=False,
                newline_closes=conf.get('newline_closes', False),
                same_tag_closes=conf.get('same_tag_closes', False),
                standalone=conf.get('standalone', False),
                render_embedded=conf.get('render_embedded', False),
                strip=conf.get('strip', False),
                swallow_trailing_newline=conf.get('swallow_trailing_newline', False)
            )

            logger.debug('Loaded simple BBCode formatter "%s" | "%s"', tag_name, conf)

    def load_complex_formatters(self):
        if self.complex_formatter_path is None:
            return

        complex_formatter_config = {}
        if self.complex_formatter_config_path is not None:
            try:
                complex_formatter_config = toml.load(self.complex_formatter_config_path)
            except FileNotFoundError:
                logger.error('Complex formatter config file not found at "%s"',
                             self.complex_formatter_config_path)

        self.bb_registry.init_complex_formatters(self.complex_formatter_path,
                                                 complex_formatter_config)

        for formatter in self.bb_registry.complex_formatters:
            self.parser.add_complex_formatter(
                tag_name=formatter['tag_name'],
                render_func=formatter['obj'].format,
                escape_html=False,
                replace_links=False,
                replace_cosmetic=False,
                newline_closes=formatter.get('newline_closes', False),
                same_tag_closes=formatter.get('same_tag_closes', False),
                standalone=formatter.get('standalone', False),
                render_embedded=formatter.get('render_embedded', True),
                strip=formatter.get('strip', False),
                swallow_trailing_newline=formatter.get('swallow_trailing_newline', False)
            )
            logger.debug('Loaded complex formatter "%s"', formatter['tag_name'])


class BBParser():
    def __init__(self, config):
        loader = BBParserLoader(BBParserCore(), BBRegistry, config)
        self.parser = loader.load_parser()

    def format(self, text, **kwargs):
        """Format BBCode text.

        Args:
            text (str): Text
        """

        return self.parser.format(text=text, **kwargs)