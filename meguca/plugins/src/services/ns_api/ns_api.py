import requests
import xmltodict

from meguca import plugin_categories
from meguca.plugins.src.services.ns_api import exceptions
from meguca.plugins.src.services.ns_api import api_helper

# Maximum number of requests sent in 30 sec
RATE_LIMIT = 50

API_URL_BEGINNING = "https://www.nationstates.net/cgi-bin/api.cgi?"
API_PARAM_DELIMITER = ";"
API_VALUE_DELIMITER = "+"


class NSApiPlugin(plugin_categories.Service):
    def get(self):
        return NSApi(self.plg_config['Auth']['useragent'],
                     self.plg_config['Auth']['password'])


class NSApi():
    def __init__(self, user_agent, password=None):
        self.session = requests.Session()

        self.user_agent = user_agent
        self.password = password

        # Number of requests sent in 30 sec range
        # to avoid rate-limit exceeding
        self.ratelimit_req_count = 0

        # Headers of API requests
        self.req_headers = {'user-agent': self.user_agent}

        if password is not None:
            self._setup_private_session()

    def _setup_private_session(self):
        """Add password into headers to obtain pin on first private shard call."""

        self.req_headers['X-Password'] = self.password

    def construct_req_url(self, api_type, name, shards, shard_params):
        """Construct an API request URL based on api_type, name, and shards."""

        params = {api_type: name, 'q': shards}
        params.update(shard_params)

        url = api_helper.construct_url(params, API_URL_BEGINNING,
                                       API_PARAM_DELIMITER,
                                       API_VALUE_DELIMITER)

        return url

    def send_api_req(self, url):
        """Send API request.

        :param url: API request URL

        :rtype: A requests.Respond object
        """

        print(self.ratelimit_req_count)
        if self.ratelimit_req_count <= RATE_LIMIT:
             respond = self.session.get(url, headers=self.req_headers)
        else:
            raise exceptions.NSAPIRateLimitError("API rate limit exceeded! Please wait a minute")

        return respond

    def set_ratelimit_req_count(self, resp):
        """Set ratelimit request count.

        :param resp: A requests.Respond object
        """
        if 'x-ratelimit-requests-seen' in resp.headers:
            self.ratelimit_req_count = int(resp.headers['x-ratelimit-requests-seen'])

    def set_pin(self, resp):
        """Add pin into request headers for next private calls.

        :param resp: A requests.Respond object
        """

        if 'X-Pin' in resp.headers:
            self.req_headers['X-Pin'] = resp.headers['X-Pin']
            # Password is not necessary anymore
            self.req_headers.pop('X-Password', None)

    def process_xml(self, resp):
        """Process XML in respond into dict.

        :param resp: A requests.Respond object

        :rtype: A dict represents the XML tree without root element
        """

        resp_dict = xmltodict.parse(resp.text)
        # Discard root XML element
        resp_dict = resp_dict[list(resp_dict.keys())[0]]

        return resp_dict

    def process_respond(self, resp):
        """Process the API respond.

        :param resp: A requests.Respond object

        :rtype: A dict represents the XML tree of the respond
        """

        self.set_ratelimit_req_count(resp)

        if resp.status_code == 200:
            self.set_pin(resp)
            return self.process_xml(resp)
        elif resp.status_code == 400:
            raise exceptions.NSAPIReqError('Empty shard causes error when get world data')
        elif resp.status_code == 404:
            raise exceptions.NSAPIReqError('This region or nation does not exist')
        elif resp.status_code == 403:
            raise exceptions.NSAPIAuthError('Incorrect password')
        elif resp.status_code == 429:
            # In case someone override the internal
            # ratelimiting mechanism
            raise exceptions.NSAPIRateLimitError('NationStates has temporarily banned you for'
                                                 'violating the rate limit.'
                                                 'Re-try after {}'.format(resp.headers['X-Retry-After']))
        elif resp.status_code == 500:
            raise exceptions.NSAPIError('NS API returned an internal server error')
        else:
            raise exceptions.NSAPIError('An unknown API error has occured')

    def get_data(self, api_type, name, shards, shard_params={}):
        """Get info from the API.

        :param api_type: Type of API (nation, region, or world)
        :param name: Name of nation/region
        :param shards: A name of a shard or list of shards
        :param shard_params: A dict represents shard parameters

        :rtype: A dict represents the XML tree of the response
        """

        url = self.construct_req_url(api_type, name, shards, shard_params)
        respond = self.send_api_req(url)

        return self.process_respond(respond)

    def get_nation(self, name, shards, shard_params={}):
        """Get info of a nation.

        :param name: Name of the nation
        :param shards: A name of a shard or list of shards
        :param shard_params: A dict represents shard parameters

        :rtype: A dict represents the XML tree of the API respond
        """

        return self.get_data('nation', name, shards, shard_params)

    def get_region(self, name, shards, shard_params={}):
        """Get info of a region.

        :param name: Name of the region
        :param shards: A name of a shard or list of shards
        :param shard_params: A dict represents shard parameters

        :rtype: A dict represents the XML tree of the API respond
        """

        return self.get_data('region', name, shards, shard_params)

    def get_world(self, shards, shard_params={}):
        """Get info of the game world.

        :param shards: A name of a shard or list of shards
        :param shard_params: A dict represents shard parameters

        :rtype: A dict represents the XML tree of the API respond
        """

        return self.get_data('', '', shards, shard_params)