import requests

from meguca import plugin_categories
from meguca.plugins.src.ns_site import helpers
from meguca.plugins.src.ns_site import exceptions


ACTION_URL = "https://www.nationstates.net/page={}"
LOCALID_URL = "https://www.nationstates.net/template-overall=none/page=settings"


class NSSitePlugin(plugin_categories.Service):
    def get(self, ns_api, config):
        if 'X-Pin' in ns_api.session.headers:
            pin = ns_api.session.headers['X-Pin']
            return NSSite(config['Meguca']['Auth']['useragent'], pin)
        else:
            raise exceptions.NSSiteSecurityError("Cannot find PIN to authenticate host nation. Consider providing login credential
                                                 "for the host nation in the general config file or disabling this plugin")


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

        self.localid = None

    def handle_errors(self, resp):
        """Handling errors if a request returns them.

        Args:
            resp (requests.Response): Respond.

        Raises:
            Refer to NS Site exceptions for the exception each type of errors may raise.
        """

        if resp.status_code != 200:
            raise exceptions.NSSiteHTTPError("""A HTTP error occured when connecting to NationStates website.
                                             HTTP status code: {}""".format(resp.status_code))

        error_parser = helpers.ErrorParser()
        error_parser.feed(resp.text)
        error = error_parser.get_error()

        if error is None:
            return
        elif "security check" in error:
            raise exceptions.NSSiteSecurityError("Security check failed. Please don't login into the "
                                                 "host nation elsewhere while the software is running.")
        elif "does not exist" in error:
            raise exceptions.NSSiteNotFound('The requested page does not exist.')
        else:
            raise exceptions.NSSiteError(error)

    def set_localid(self):
        """Set local ID for a request."""

        resp = self.session.get(LOCALID_URL)
        self.handle_errors(resp)

        parser = helpers.LocalIdParser()
        parser.feed(resp.text)

        self.localid = parser.get_id()

    def execute(self, action, params):
        """Send a POST request."""

        params['localid'] = self.localid
        url = ACTION_URL.format(action)

        resp = self.session.post(url, data=params)
        self.handle_errors(resp)



