"""Generate law dispatch templates from forum's archive.
"""

import os
import logging

import requests
import toml
import bs4

from meguca import plugin_categories


logger = logging.getLogger(__name__)

LAWS_PLACEHOLDER = '[laws]'


def get_bb_tag(html_tag, lut):
    """Get matching BBCode tags from HTML.

    Args:
        tag (bs4.Tag): HTML tag.
        lut (list): BBCode lookup table.

    Returns:
        str: BBCode tag.
    """

    for key, tag in lut.items():
        if html_tag.name == tag['name'] and html_tag.attrs == tag['attrs']:
            return tag['bb_tag']

    return '{text}'


def gen_bbcode(soup, lut, line_break_html_tag, default_bb_tag):
    """Generate BBCode tags from HTML.

    Args:
        soup (bs4.BeautifulSoup): HTML elements.
        lut ([type]): BBCode lookup table.
        line_break_html_tag (str): Tag represents a line break.
        default_bb_tag (str): Default tag if lookup failed.
    """

    bbcode = ''

    for content in soup.children:
        if content.name == line_break_html_tag:
            bbcode += '\n'
        elif isinstance(content, bs4.Tag):
            text = gen_bbcode(content, lut, line_break_html_tag, default_bb_tag)
            bb_tag = get_bb_tag(content, lut)
            bbcode += bb_tag.format(text=text)
        elif isinstance(content, str) and not content.isspace():
            bb_tag = default_bb_tag
            bbcode += bb_tag.format(text=content.strip('\n').strip())

    return bbcode


def embed_jinja_template(bbcode, std_template_path):
    """Embed standard Jinja template into laws dispatches.

    Args:
        bbcode (str): BBCode text.
        std_template_path (str): Standard Jinja template file path.

    Returns:
        str: BBCode text with Jinja template embedded.
    """

    try:
        with open(std_template_path) as f:
            return f.read().replace(LAWS_PLACEHOLDER, bbcode)
    except FileNotFoundError:
        raise FileNotFoundError('Could not find standard laws dispatch template file.')


class LawsUpdater(plugin_categories.Collector):
    def run(self):
        self.update_dispatch_config()
        self.update_laws_dispatches()

    def dry_run(self):
        self.update_dispatch_config()
        self.update_laws_dispatches()

    def update_dispatch_config(self):
        """Update laws dispatch config file.
        """

        conf = self.plg_config['general']
        dispatch_config = {}

        for name, info in self.plg_config['laws'].items():
            dispatch_config[name] = {'title': info['title'],
                                     'category': conf['category'],
                                     'sub_category': conf['sub_category']}

        with open(conf['dispatch_config_path'], 'w') as f:
            toml.dump(dispatch_config, f)

        logger.info('Dispatch config updated')

    def update_laws_dispatches(self):
        """Update laws dispatch files.
        """

        conf = self.plg_config['general']
        s = requests.Session()

        for name, info in self.plg_config['laws'].items():
            html = s.get(info['url']).text
            bbcode = self.get_bbcode_laws(html)

            filename = '{}.{}'.format(name, conf['template_ext'])
            file_path = os.path.join(conf['template_dir_path'], filename)
            with open(file_path, 'w') as f:
                f.write(bbcode)

            logger.info('Generated laws dispatch "%s"', name)

    def get_bbcode_laws(self, html):
        """Convert forum's html into bbcode.

        Args:
            html (str): HTML text.

        Returns:
            str: BBCode text.
        """

        bb_conf = self.plg_config['bb_lookup']
        soup = bs4.BeautifulSoup(html, 'html.parser')
        container = soup.select(bb_conf['container'])[0]
        bbcode = gen_bbcode(container, bb_conf['tags'],
                            bb_conf['line_break_html_tag'],
                            bb_conf['default_bb_tag'])

        return embed_jinja_template(bbcode, self.plg_config['general']['std_template_path'])
