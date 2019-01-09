import requests
import xmltodict

from meguca import plugin_categories
from meguca.plugins.src.services.ns_api import exceptions
from meguca.plugins.src.services.ns_api import helpers

# Maximum number of requests sent in 30 sec
RATE_LIMIT = 50

API_URL_BEGINNING = "https://www.nationstates.net/cgi-bin/api.cgi?"
API_PARAM_DELIMITER = ";"
API_VALUE_DELIMITER = "+"


class NSApiPlugin(plugin_categories.Service):
    def get(self, config):

        if 'password' in config['Meguca']['Auth']:
            ns_api = NSApi(config['Meguca']['Auth']['useragent'],
                           config['Meguca']['Auth']['password'])
            ns_api.get_nation(config['Meguca']['Auth']['loginnation'], 'ping')
        else:
            ns_api = NSApi(config['Meguca']['Auth']['useragent'])

        return ns_api


class NSApi():
    def __init__(self, user_agent, password=None):
        self.session = requests.Session()
        self.session.headers['user-agent'] = user_agent
        self.password = password

        # Number of requests sent in 30 sec range
        # to avoid rate-limit exceeding
        self.ratelimit_req_count = 0

        if password is not None:
            self.setup_private_session()

    def setup_private_session(self):
        """Add password into headers to obtain pin on first private shard call."""

        self.session.headers.update({'X-Password': self.password})

    def construct_req_url(self, api_type, name, shards, shard_params):
        """Construct a request URL based on api_type, name, and shards."""

        params = {api_type: name, 'q': shards}
        params.update(shard_params)

        url = helpers.construct_url(params, API_URL_BEGINNING,
                                    API_PARAM_DELIMITER,
                                    API_VALUE_DELIMITER)

        return url

    def send_req(self, url):
        """Send request."""

        if self.ratelimit_req_count <= RATE_LIMIT:
             resp = self.session.get(url)
        else:
            raise exceptions.NSAPIRateLimitError("API rate limit exceeded! Please wait a minute")

        return resp

    def set_ratelimit_req_count(self, resp):
        """Set ratelimit request count."""

        if 'x-ratelimit-requests-seen' in resp.headers:
            self.ratelimit_req_count = int(resp.headers['x-ratelimit-requests-seen'])

    def set_pin(self, resp):
        """Add pin into request headers for next private calls."""

        if 'X-Pin' in resp.headers:
            self.session.headers['X-Pin'] = resp.headers['X-Pin']
            # Password is not necessary anymore
            self.session.headers.pop('X-Password', None)

    def process_xml(self, resp):
        """Convert the XML in respond into dict."""

        resp_dict = xmltodict.parse(resp.text)
        # Discard root XML element
        resp_dict = resp_dict[list(resp_dict.keys())[0]]

        return resp_dict

    def process_respond(self, resp):
        """Process the respond."""

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

    def get_data(self, api_type="", name="", shards="", shard_params=None):
        """Get info.

        Args:
            api_type (str, optional): API type (nation/region/wa)
                Don't use if wanting world data.
            name (str, optional): Name of nation/region
                Don't use if wanting WA or world data.
            shards (str|list): Shard to request
                Use a list for multiple shards.
            shard_params (dict, optional): Shard parameters

        Returns:
            dict: XML tree of the respond

        Examples:
            Get the population of a nation:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_nation('testlandia', 'population')
            >>> r['POPULATION']
            '33107'

            Get the population and motto of a nation:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_data('nation', 'testlandia', ['population', 'motto'])
            >>> r['POPULATION']
            '33107'
            >>> r['MOTTO']
            'Grr. Arg.'

            Get the average endorsement count and influence of the world:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_data(shards='census', params={'scale': ['66', '65'], 'mode': 'score'})
            >>> r['CENSUS']['SCALE'][0]['SCORE']
            '3.34'
            >>> r['CENSUS']['SCALE'][1]['SCORE']
            '1833.28'
        """


        url = self.construct_req_url(api_type, name, shards, shard_params or {})
        respond = self.send_req(url)

        return self.process_respond(respond)

    def get_nation(self, name, shards, shard_params=None):
        """Get info of a nation.

        Args:
            name (str): Name of nation
            shards (str|list): Shard to request
                Use a list for multiple shards.
            shard_params (dict, optional): Shard parameters

        Returns:
            dict: XML tree of the respond

        Examples:
            Get the population of a nation.

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_nation('testlandia', 'population')
            >>> r['POPULATION']
            '33107'

            Get the population and motto of a nation:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_data('nation', 'testlandia', ['population', 'motto'])
            >>> r['POPULATION']
            '33107'
            >>> r['MOTTO']
            'Grr. Arg.'

            Get the endorsement count and influence of a nation:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_data('nation', 'testlandia', 'census', {'scale': ['66', '65'], 'mode': 'score'})
            >>> r['CENSUS']['SCALE'][0]['SCORE']
            '0.00'
            >>> r['CENSUS']['SCALE'][1]['SCORE']
            '12345.0'
        """

        return self.get_data('nation', name, shards, shard_params)

    def get_region(self, name, shards, shard_params=None):
        """Get info of a region.

        Args:
            name (str): Name of region
            shards (str|list): Shard to request
                Use a list for multiple shards.
            shard_params (dict, optional): Shard parameters

        Returns:
            dict: XML tree of the respond

        Examples:
            Get the name of a region:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_region('the_south_pacific', 'name')
            >>> r['NAME']
            'the South Pacific'

            Get the nation number and founder of a region:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_region('the_south_pacific', ['numnations', 'founder'])
            >>> r['NUMNATIONS']
            '7250'
            >>> r['FOUNDER']
            '0'

            Get the average endorsement count and influence of a region:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_region('the_south_pacific', 'census', {'scale': ['66', '65'], 'mode': 'score'})
            >>> r['CENSUS']['SCALE'][0]['SCORE']
            '8.12'
            >>> r['CENSUS']['SCALE'][1]['SCORE']
            '17776.3'
        """

        return self.get_data('region', name, shards, shard_params)

    def get_wa(self, council, shards, shard_params=None):
        """Get info of the World Assembly.

        Args:
            council (str): Council name
                ga -- General Assembly
                sc -- Security Council
            shards (str|list): Shard to request
                Use a list for multiple shards.
            shard_params (dict, optional): Shard parameters

        Returns:
            dict: XML tree of the respond

        Examples:
            Get the current GA resolution:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_wa('ga', 'resolution')
            >>> r['RESOLUTION']['NAME']
            'Sensible limits on industry act'

            Get delegates and WA members:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_wa('ga', ['delegates', 'members'])
            >>> r['DELEGATES']
            'erinor,tsunamy,fedele,siwale'
            >>> r['MEMBERS']
            'usovietnam,roavin,serres,queen_yuno'
        """

        if council == 'ga':
            api_type = 'wa=1'
        elif council == 'sc':
            api_type = 'wa=2'

        return self.get_data(api_type, '', shards, shard_params)

    def get_world(self, shards, shard_params=None):
        """Get info of the world.

        Args:
            name (str): Name of region
            shards (str|list): Shard to request
                Use a list for multiple shards.
            shard_params (dict, optional): Shard parameters

        Returns:
            dict: XML tree of the respond

        Examples:
            Get the total number of nations in NationStates:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_world('numnations')
            >>> r['NAME']
            '199000'

            Get the number of regions and region names in NationStates:

            >>> ns_api = NSApi('Lampshade')
            >>> ns_api.get_world(['regions', 'numregions'])
            >>> r['REGIONS']
            'the_south_pacific,the_east_pacific,japan'
            >>> r['NUMREGIONS']
            '12220'

            Get 5 founding and CTE events:

            >>> ns_api = NSApi('Lampshade')
            >>> r = ns_api.get_world('happenings', {'filter': ['founding', 'cte'], 'limit': '5'})
            >>> r['HAPPENINGS']['EVENT'][0]['TEXT']
            '@@homura_chan@@ was founded in %%the_east_pacific%%.
        """

        return self.get_data('', '', shards, shard_params)