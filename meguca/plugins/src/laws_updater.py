"""Generate law dispatch templates from forum's archive.
"""

import os
import logging
import re
import unicodedata
import time

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


class GenAnchor():
    """Generate anchor tags based on laws sections and articles.

    Args:
        lut (dict): Anchor link lookup table.
    """

    def __init__(self, lut):
        sec_conf = lut['section']
        self.sec_regex = re.compile(sec_conf['match'])
        self.sec_rep = sec_conf['anchor_link']
        art_conf = lut['article']
        self.art_regex = re.compile(art_conf['match'])
        self.art_rep = art_conf['anchor_link']
        ss_conf = lut['subsection']
        self.ss_regex = re.compile(ss_conf['match'])
        self.ss_rep = ss_conf['anchor_link']

        self.art = ""
        self.sec = ""

    def get_anchor(self, text):
        """Get anchor tag from law's text line

        Args:
            text (str): Text.

        Returns:
            str: Anchor tag.
                 Returns None if no anchor tag can be generated.
        """

        if self.sec_regex.search(text):
            sec = self.sec_regex.sub(self.sec_rep, text)
            self.sec = sec
            link = '{}_{}'.format(self.art, sec)
        elif self.ss_regex.search(text):
            ss = self.ss_regex.sub(self.ss_rep, text)
            link = '{}_{}_{}'.format(self.art, self.sec, ss)
        elif self.art_regex.search(text):
            art = self.art_regex.sub(self.art_rep, text)
            self.art = art
            link = art
        else:
            return None

        return '[anchor={}][/anchor]'.format(link)


def gen_bbcode(soup, lut, gen_anchor, line_break_html_tag, default_bb_tag):
    """Generate BBCode tags from HTML.

    Args:
        soup (bs4.BeautifulSoup): HTML elements.
        lut (dict): BBCode lookup table.
        gen_anchor: Anchor generation.
        line_break_html_tag (str): Tag represents a line break.
        default_bb_tag (str): Default tag if lookup failed.
    """

    bbcode = ''

    for content in soup.children:
        if content.name == line_break_html_tag:
            bbcode += '\n'
        elif isinstance(content, bs4.Tag):
            text = gen_bbcode(content, lut, gen_anchor,
                              line_break_html_tag, default_bb_tag)
            bb_tag = get_bb_tag(content, lut)
            bbcode += bb_tag.format(text=text)
        elif isinstance(content, str):
            if content.isspace():
                bbcode += content
            else:
                text = content.replace('\n', '')
                # Get rid of non-break space.
                clean_text = unicodedata.normalize('NFKD', text.strip())
                anchor = gen_anchor.get_anchor(clean_text)
                if anchor is not None:
                    bbcode += anchor
                bbcode += default_bb_tag.format(text=text)

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
        laws = self.update_dispatch_config()
        self.update_laws_dispatches()

        return {'laws': laws}

    def update_dispatch_config(self):
        """Update laws dispatch config file.
        """

        conf = self.plg_config['general']
        dispatch_config = {}

        laws = {}
        for name, info in self.plg_config['laws'].items():
            dispatch_config[name] = {'title': info['title'],
                                     'category': conf['category'],
                                     'sub_category': conf['sub_category']}
            laws[name] = info['title']

        with open(conf['dispatch_config_path'], 'w') as f:
            toml.dump(dispatch_config, f)

        logger.info('Dispatch config updated')
        return laws

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
            time.sleep(2)

    def get_bbcode_laws(self, html):
        """Convert forum's html into bbcode.

        Args:
            html (str): HTML text.

        Returns:
            str: BBCode text.
        """

        gen_anchor = GenAnchor(self.plg_config['anchor_lookup'])
        bb_conf = self.plg_config['bb_lookup']
        soup = bs4.BeautifulSoup(html, 'html.parser')
        container = soup.select(bb_conf['container'])[0]
        bbcode = gen_bbcode(container, bb_conf['tags'], gen_anchor,
                            bb_conf['line_break_html_tag'],
                            bb_conf['default_bb_tag'])

        return embed_jinja_template(bbcode, self.plg_config['general']['std_template_path'])
