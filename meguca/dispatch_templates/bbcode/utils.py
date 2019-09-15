"""Utility functions for some BBCode tags.
"""

import re
import logging


logger = logging.getLogger(__name__)


DISPATCH_URL = 'https://www.nationstates.net/page=dispatch/id='

def get_url(url, custom_vars_urls, dispatches):
    """Get real URL from special URL if needed.

    Args:
        url (str): Input URL.
        custom_vars_urls (dict): URLs in custom vars file.
        dispatches (dict): Dispatch configurations.

    Returns:
        str: Real URL.
    """

    if url in custom_vars_urls:
        r = custom_vars_urls[url]
    elif url in dispatches:
        dispatch_id = dispatches[url]['id']
        r = '{}{}'.format(DISPATCH_URL, dispatch_id)
    elif url.split('#')[0] in dispatches:
        url = url.split('#')
        dispatch_id = dispatches[url[0]]['id']
        r = '{}{}#{}'.format(DISPATCH_URL, dispatch_id, url[1])
    else:
        r = url

    return r


def build_names_lut(laws):
    """Get law name lookup table for quick access.

    Args:
        laws (dict): Laws configuration.
    """

    lut = {}
    for name, config in laws.items():
        if 'alt_names' in config:
            lut.update({alt_name.lower(): name for alt_name in config['alt_names']})

    return lut


def get_base_url(text, names_lut, dispatch_info):
    """Get base URL of law dispatch from law name.

    Args:
        text (str): Law name
        names_lut (dict): Law name lookup table.

    Returns:
        str: Base URL.
    """

    name = text.lower()
    if name.find('the ') == 0:
        name = name.replace('the ', '', 1)

    if name in names_lut:
        name = names_lut[name]

    name = name.replace(' ', '_')
    if name in dispatch_info:
        dispatch_id = dispatch_info[name]['id']
        return '{}{}'.format(DISPATCH_URL, dispatch_id)

    print(name)
    logger.warning('Law "%s" not found in storage', text)
    return None


def get_laws_url(text, config, names_lut, dispatch_info):
    url = ""
    pattern = re.compile(config['citation_pattern'])
    r = pattern.search(text)

    law = r.group('law')
    if law:
        base_url = get_base_url(law, names_lut, dispatch_info)
        if base_url:
            url += base_url

    article = r.group('art')
    section = r.group('sec')
    if article:
        url += '#'
        url += config['article_format'].format(article)
    if section:
        url += config['section_format'].format(section)

    return url