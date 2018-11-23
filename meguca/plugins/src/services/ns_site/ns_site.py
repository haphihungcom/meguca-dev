import requests

from meguca import plugin_categories
from meguca import utils
from meguca.plugins.src.services.ns_site import helpers
from meguca.plugins.src.services.ns_site import exceptions

ACTION_URL = "https://www.nationstates.net/page={}"
LOCALID_URL = "https://www.nationstates.net/template-overall=none/page=settings"


class NSSitePlugin(plugin_categories.Service):
    def get(self, ns_api):
        if 'X-Pin' in ns_api.session.headers:
            pin = ns_api.session.headers['X-Pin']

        return NSSite(self.plg_config['Auth']['useragent'], pin)


class NSSite():
    def __init__(self, user_agent, pin=None):
        self.session = requests.Session()

        self.session.headers.update({'user-agent': user_agent})
        self.session.cookies.update({'pin': pin})

        self.localid = None

    def handle_errors(self, resp):
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
        resp = self.session.get(LOCALID_URL)
        self.handle_errors(resp)

        parser = helpers.LocalIdParser()
        parser.feed(resp.text)

        self.localid = parser.get_id()

    def execute(self, action, params):
        params['localid'] = self.localid
        url = ACTION_URL.format(action)

        resp = self.session.post(url, data=params)
        self.handle_errors(resp)



