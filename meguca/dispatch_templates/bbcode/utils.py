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

    # Handle special URLs
    if 'https://' not in url:
        # URLs in custom vars file take precedent
        if url in custom_vars_urls:
            real_url = custom_vars_urls[url]
        elif url in dispatches:
            dispatch_id = dispatches[url]['id']
            real_url = 'https://www.nationstates.net/page=dispatch/id={}'.format(dispatch_id)
        else:
            real_url = url
    else:
        real_url = url

    return real_url