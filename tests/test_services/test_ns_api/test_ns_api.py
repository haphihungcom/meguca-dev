from unittest import mock

import pytest
import requests

from meguca.plugins.services.ns_api import ns_api
from meguca.plugins.services.ns_api import api_helper
from meguca.plugins.services.ns_api import exceptions

USER_AGENT = "Unit tests of Meguca | NS API Wrapper component"

class TestNSApiLowLevel():
    """Unit tests for NSApi low-level methods."""

    def test_setup_private_session(self):
        api = ns_api.NSApi("", 'Test')
        api._setup_private_session()

        assert api.req_headers['X-Password'] == 'Test'

    def test_construct_req_url(self):

        api = ns_api.NSApi("")
        url = api.construct_req_url('Test', 'Test', 'Test', {'Test2': 'Test'})

        assert url == 'https://www.nationstates.net/cgi-bin/api.cgi?Test=Test;q=Test;Test2=Test;'

    def test_set_ratelimit_req_count(self):
        mocked_resp = mock.Mock(headers={'x-ratelimit-requests-seen': '0'})
        api = ns_api.NSApi("")

        api.set_ratelimit_req_count(mocked_resp)

        assert api.ratelimit_req_count == 0

    @mock.patch('requests.Session.get', return_value='Test')
    def test_send_api_req(self, mocked_requests_session_get):
        api = ns_api.NSApi("")

        assert api.send_api_req('Test') == 'Test'

    @mock.patch('requests.Session.get', return_value=mock.Mock(headers={'x-ratelimit-requests-seen': '0'}))
    def test_send_api_req_when_ratelimit_exceeded(self, mocked_request_session_get):
        ns_api.RATE_LIMIT = 0
        api = ns_api.NSApi("")
        api.ratelimit_req_count = 1

        with pytest.raises(exceptions.NSAPIRateLimitError):
            api.send_api_req('Test')

    def test_set_pin(self):
        mocked_resp = mock.Mock(headers={'X-Pin': '0'})
        api = ns_api.NSApi("")
        api.req_headers['X-Password'] = '0'

        api.set_pin(mocked_resp)

        assert api.req_headers['X-Pin'] == '0'
        assert 'X-Password' not in api.req_headers

    def test_process_xml(self):
        mocked_resp = mock.Mock(text='<A><a>homuraisbestgirl</a></A>')
        api = ns_api.NSApi("")

        assert api.process_xml(mocked_resp) == {'a': 'homuraisbestgirl'}

    def test_process_respond_with_status_code_200(self):
        mocked_resp = mock.Mock(status_code=200, text='<A><a>homuraisbestgirl</a></A>',
                                headers={'x-ratelimit-requests-seen': '0'})
        api = ns_api.NSApi("")

        assert api.process_respond(mocked_resp) == {'a': 'homuraisbestgirl'}

    @pytest.mark.parametrize('status_code, expected_exception', [
        (400, exceptions.NSAPIReqError),
        (404, exceptions.NSAPIReqError),
        (403, exceptions.NSAPIAuthError),
        (429, exceptions.NSAPIRateLimitError),
        (500, exceptions.NSAPIError),
        (900, exceptions.NSAPIError)
    ])
    def test_process_respond_with_error_status_code(self, status_code, expected_exception):
        mocked_resp = mock.Mock(status_code=status_code, headers={'X-Retry-After': '0'})
        api = ns_api.NSApi("")

        with pytest.raises(expected_exception):
            api.process_respond(mocked_resp)

@mock.patch('requests.Session.get',
                return_value=mock.Mock(status_code=200,
                                       text='<A><a>homuraisbestgirl</a></A>',
                                       headers={'x-ratelimit-requests-seen': '0'}))
class TestNSApi():
    """Tests for NSApi high-level methods."""

    def test_get_data_with_shard_params(self, mocked_session_get):
        api = ns_api.NSApi("")

        assert api.get_data('Test', 'Test', 'Test', {'Test2': 'Test'}) == {'a': 'homuraisbestgirl'}

    def test_get_nation(self, mocked_session_get):
        api = ns_api.NSApi("")
        result = api.get_nation('Test', shards='name')

        assert result == {'a': 'homuraisbestgirl'}

    def test_get_region(self, mocked_session_get):
        api = ns_api.NSApi("")
        result = api.get_region('Test', shards='name')

        assert result == {'a': 'homuraisbestgirl'}

    def test_get_world(self, mocked_session_get):
        api = ns_api.NSApi("")
        result = api.get_world(shards='wa')

        assert result == {'a': 'homuraisbestgirl'}


class TestNSApiAuth():
    """Tests for NSApi authentication system"""

    def test_init_no_password(self):
        api = ns_api.NSApi("")

        assert 'X-Password' not in api.req_headers

    def test_init_with_password(self):
        api = ns_api.NSApi("", password='Test')

        assert api.req_headers['X-Password'] == 'Test'

    @mock.patch('requests.Session.get', return_value=mock.Mock(status_code=200,
                text='<A><a>a</a></A>', headers={'X-Pin': '0', 'x-ratelimit-requests-seen': '0'}))
    def test_pin_auth(self, mocked_request_session_get):
        api = ns_api.NSApi("", password='Test')
        api.get_data('test', 'Test', 'test')
        api.get_data('test', 'Test', 'test')

        assert api.req_headers['X-Pin'] == '0' and 'X-Password' not in api.req_headers


class TestNSApiRateLimiter():
    """Tests for NSApi rate limiting mechanism."""

    @mock.patch('requests.Session.get', return_value=mock.Mock(status_code=200,
                text='<A><a>a</a></A>', headers={'x-ratelimit-requests-seen': '2'}))
    def test_get_data_with_ratelimit_exceeded(self, mocked_request_session_get):
        ns_api.RATE_LIMIT = 1
        api = ns_api.NSApi("")
        api.get_data('Test','Test', 'Test')

        with pytest.raises(exceptions.NSAPIRateLimitError):
            api.get_data('Test','Test', 'Test')


class TestNSApiIntegration():
    """Tests for NSApi high-level methods. Real API is used."""

    def test_get_nation(self):
        api = ns_api.NSApi(USER_AGENT)

        assert api.get_nation('Testlandia', 'name')['NAME'] == 'Testlandia'

    def test_get_region(self):
        api = ns_api.NSApi(USER_AGENT)

        assert api.get_region('Testregionia', 'name')['NAME'] == 'Testregionia'

    def test_get_world(self):
        api = ns_api.NSApi(USER_AGENT)

        assert api.get_world('lasteventid')['LASTEVENTID']



