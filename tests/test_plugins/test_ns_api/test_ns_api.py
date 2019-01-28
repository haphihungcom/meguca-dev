from unittest import mock

import pytest
import requests

from meguca.plugins.src.ns_api import ns_api
from meguca.plugins.src.ns_api import exceptions


USER_AGENT = "Unit tests of Meguca | NS API Wrapper component"


def get_ns_api(user_agent="", password=None, **kwargs):
    api = ns_api.NSApi(user_agent, password)
    if kwargs is not None:
        api.respond = mock.Mock(**kwargs)

    return api


class TestNSApiLowLevel():
    """Unit tests for NSApi low-level methods."""

    def test_setup_private_session(self):
        api = ns_api.NSApi("", 'Test')
        api.setup_private_session()

        assert api.session.headers['X-Password'] == 'Test'

    def test_set_req_count(self):
        api = get_ns_api(headers={'x-ratelimit-requests-seen': '0'})

        api.set_req_count()

        assert api.req_count == 0

    @mock.patch('requests.Session.get', return_value='Test')
    def test_send_req(self, mocked_requests_session_get):
        api = ns_api.NSApi("")

        api.send_req('Test')

        assert api.respond == 'Test'

    @mock.patch('requests.Session.get', return_value=mock.Mock(headers={'x-ratelimit-requests-seen': '0'}))
    def test_send_req_when_ratelimit_exceeded(self, mocked_request_session_get):
        ns_api.RATE_LIMIT = 0
        api = get_ns_api()
        api.req_count = 1

        with pytest.raises(exceptions.NSAPIRateLimitError):
            api.send_req('Test')

    def test_set_pin(self):
        api = get_ns_api(headers={'X-Pin': '0'})
        api.session.headers['X-Password'] = '0'

        api.set_pin()

        assert api.session.headers['X-Pin'] == '0'
        assert 'X-Password' not in api.session.headers

    def test_process_xml(self):
        api = get_ns_api(text='<A><a>homuraisbestgirl</a></A>')

        assert api.process_xml() == {'a': 'homuraisbestgirl'}

    def test_process_respond_with_status_code_200(self):
        api = get_ns_api(status_code=200, text='<A><a>homuraisbestgirl</a></A>',
                         headers={'x-ratelimit-requests-seen': '0'})


        assert api.get_respond() == {'a': 'homuraisbestgirl'}

    @pytest.mark.parametrize('status_code, expected_exception', [
        (400, exceptions.NSAPIReqError),
        (404, exceptions.NSAPIReqError),
        (403, exceptions.NSAPIAuthError),
        (429, exceptions.NSAPIRateLimitError),
        (500, exceptions.NSAPIError),
        (900, exceptions.NSAPIError)
    ])
    def test_process_respond_with_error_status_code(self, status_code, expected_exception):
        mocked_resp = mock.Mock()
        api = get_ns_api(status_code=status_code, headers={'X-Retry-After': '0'})

        with pytest.raises(expected_exception):
            api.get_respond()

@mock.patch('requests.Session.get',
            return_value=mock.Mock(status_code=200,
                                   text='<A><a>homuraisbestgirl</a></A>',
                                   headers={'x-ratelimit-requests-seen': '0'}))
class TestNSApi():
    """Tests for NSApi high-level methods."""

    def test_get_data_with_shard_params(self, mocked_session_get):
        api = get_ns_api()

        assert api.get_data('Test', 'Test', 'Test', {'Test2': 'Test'}) == {'a': 'homuraisbestgirl'}

    def test_get_nation(self, mocked_session_get):
        api = get_ns_api()

        result = api.get_nation('Test', shards='name')

        assert result == {'a': 'homuraisbestgirl'}

    def test_get_region(self, mocked_session_get):
        api = get_ns_api()
        result = api.get_region('Test', shards='name')

        assert result == {'a': 'homuraisbestgirl'}

    def test_get_world(self, mocked_session_get):
        api = get_ns_api()
        result = api.get_world(shards='wa')

        assert result == {'a': 'homuraisbestgirl'}


class TestNSApiAuth():
    """Tests for NSApi authentication system"""

    def test_init_no_password(self):
        api = get_ns_api()

        assert 'X-Password' not in api.session.headers

    def test_init_with_password(self):
        api = get_ns_api(password='Test')

        assert api.session.headers['X-Password'] == 'Test'

    @mock.patch('requests.Session.get',
                return_value=mock.Mock(status_code=200,
                                       text='<A><a>a</a></A>',
                                       headers={'X-Pin': '0',
                                                'x-ratelimit-requests-seen': '0'}))
    def test_pin_auth(self, mocked_request_session_get):
        api = get_ns_api(password='Test')

        api.get_data('test', 'Test', 'test')
        api.get_data('test', 'Test', 'test')

        assert api.session.headers['X-Pin'] == '0' and 'X-Password' not in api.session.headers


class TestNSApiRateLimiter():
    """Tests for NSApi rate limiting mechanism."""

    @mock.patch('requests.Session.get',
                return_value=mock.Mock(status_code=200,
                                       text='<A><a>a</a></A>',
                                       headers={'x-ratelimit-requests-seen': '2'}))
    def test_get_data_with_ratelimit_exceeded(self, mocked_request_session_get):
        ns_api.RATE_LIMIT = 1
        api = ns_api.NSApi("")
        api.get_data('Test','Test', 'Test')

        with pytest.raises(exceptions.NSAPIRateLimitError):
            api.get_data('Test','Test', 'Test')


class TestNSApiIntegration():
    """Tests for NSApi high-level methods. Real API is used."""

    def test_get_nation(self):
        api = get_ns_api(USER_AGENT)

        assert api.get_nation('Testlandia', 'name')['NAME'] == 'Testlandia'

    def test_get_region(self):
        api = get_ns_api(USER_AGENT)

        assert api.get_region('Testregionia', 'name')['NAME'] == 'Testregionia'

    def test_get_world(self):
        api = get_ns_api(USER_AGENT)

        assert api.get_world('lasteventid')['LASTEVENTID']


class TestNSApiPlugin():
    @mock.patch('requests.Session.get',
                return_value=mock.Mock(headers={'X-Pin': '0'},
                                       status_code=200,
                                       text='<A><a>a</a></A>'))
    def test_get_with_password(self, mocked_requests_session_get):
        plg = ns_api.NSApiPlugin()
        config = {'Auth': {'UserAgent': 'Test', 'Password': 'password', 'HostNation': 'Test'}}

        api = plg.get(config={'Meguca': config})

        assert api.session.headers['user-agent'] == 'Test' and api.session.headers['X-Pin'] == '0'

    def test_get_without_password(self):
        plg = ns_api.NSApiPlugin()
        config = {'Auth': {'UserAgent': 'Test', 'HostNation': 'Test'}}

        api = plg.get(config={'Meguca': config})

        assert api.session.headers['user-agent'] == 'Test'



