"""Utility functions for some BBCode tags.
"""

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
        r = 'https://www.nationstates.net/page=dispatch/id={}'.format(dispatch_id)
    elif url.split('#')[0] in dispatches:
        url = url.split('#')
        dispatch_id = dispatches[url[0]]['id']
        r = 'https://www.nationstates.net/page=dispatch/id={}#{}'.format(dispatch_id, url[1])
    else:
        r = url

    return r