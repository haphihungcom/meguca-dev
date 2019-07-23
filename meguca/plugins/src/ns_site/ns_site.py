"""An interface to send POST requests to NationStates.
"""


import logging

import requests

from meguca import plugin_categories
from meguca.plugins.src.ns_site import helpers
from meguca.plugins.src.ns_site import exceptions


logger = logging.getLogger(__name__)


ACTION_URL = "https://www.nationstates.net/page={}"
LOCALID_URL = "https://www.nationstates.net/template-overall=none/page=settings"


class NSSitePlugin(plugin_categories.Service):
    def get(self, ns_api, config):
        if 'X-Pin' in ns_api.session.headers:
            pin = ns_api.session.headers['X-Pin']
            ns_site = NSSite(config['meguca']['auth']['user_agent'], pin)
            ns_site.set_localid()

            return ns_site
        else:
            raise exceptions.NSSiteSecurityError('Cannot find PIN to authenticate host nation. Consider providing login credential '
                                                 'for the host nation in the general config file or disabling this plugin')


class NSSite():
    """Provide a way to send POST requests with local ID to NationStates main site.
    Is primarily used to update dispatches.

    Args:
        user_agent (str): User agent
        pin (str): Defaults to None. PIN number to authenticate requests.
    """

    def __init__(self, user_agent, pin):
        self.session = requests.Session()

        self.session.headers['user-agent'] = user_agent
        self.session.cookies['pin'] = pin

    def set_localid(self):
        """Set local ID for a request."""

        resp = self.session.get(LOCALID_URL)
        helpers.handle_errors(resp)

        self.localid = helpers.get_localid(resp.text)

        logger.debug('Set local ID: %s', self.localid)

    def execute(self, action, params):
        """Send a POST request."""

        params['localid'] = self.localid
        url = ACTION_URL.format(action)

        resp = self.session.post(url, data=params)

        logger.debug('Sent POST request with parameters: %r', params)

        helpers.handle_errors(resp)

        return resp.text
