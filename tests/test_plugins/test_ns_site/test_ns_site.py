from unittest import mock

import pytest

from meguca.plugins.src.ns_site import ns_site
from meguca.plugins.src.ns_site import exceptions


class TestNSSite():
    @mock.patch('requests.Session.get',
                return_value=mock.Mock(status_code=200,
                                       text='<input type="hidden" name="localid" value="123456">'))
    def test_set_localid_with_html_contains_localid_attr_in_input_tag(self, requests_session_get):
        ins = ns_site.NSSite('', '')

        ins.set_localid()

        assert ins.localid == "123456"

    @mock.patch('requests.Session.post',
                return_value=mock.Mock(status_code=200,
                                       text=''))
    def test_execute_send_post_request(self, requests_session_post):
        ins = ns_site.NSSite('', '')
        ins.localid = '12345'

        ins.execute('abc', {'ex_param': 'ex_val'})

        requests_session_post.assert_called_with('https://www.nationstates.net/page=abc',
                                               data={'ex_param': 'ex_val', 'localid': '12345'})


class TestIntegrationNSSite():
    @pytest.fixture(scope='class')
    def mock_ns_api(self):
        ns_api = mock.Mock(session=mock.Mock(headers={'X-Pin': '12345'}))

        return ns_api

    @mock.patch('requests.Session.get',
                return_value=mock.Mock(status_code=200,
                                       text='<input type="hidden" name="localid" value="67890">'))
    def test_init_get_pin_from_ns_api_and_set_localid(self, mock_request_get, mock_ns_api):
        plg = ns_site.NSSitePlugin()
        config = {'auth': {'user_agent': 'Test'}}

        ins = plg.get(ns_api=mock_ns_api, config={'meguca': config})

        assert ins.session.cookies['pin'] == '12345'
        assert ins.localid == '67890'

    def test_raise_exception_no_pin_provided(self):
        plg = ns_site.NSSitePlugin()
        config = {'Auth': {'UserAgent': ''}}
        ns_api = mock.Mock(session=mock.Mock(headers={}))

        with pytest.raises(exceptions.NSSiteSecurityError):
            plg.get(ns_api=ns_api, config={'Meguca': config})

    def test_send_dispatch_update_request(self, mock_ns_api):
        plg = ns_site.NSSitePlugin()
        config = {'auth': {'user_agent': 'Test'}}

        with mock.patch('requests.Session.get',
                        return_value=mock.Mock(status_code=200,
                                               text='<input type="hidden" name="localid" value="li42rYLF326ZS">')):
            ins = plg.get(ns_api=mock_ns_api, config={'meguca': config})

        with mock.patch('requests.Session.post',
                        return_value=mock.Mock(status_code=200,
                                               text='')) as requests_session_post:
            ins.execute('lodge_dispatch',
                        {'edit': '123',
                         'category': '8',
                         '8': '3',
                         'dname': 'ex',
                         'message': 'abc',
                         'submitbutton': '1'})

            requests_session_post.assert_called_with('https://www.nationstates.net/page=lodge_dispatch',
                                                     data={'localid': 'li42rYLF326ZS',
                                                           'edit': '123',
                                                           'category': '8',
                                                           '8': '3',
                                                           'dname': 'ex',
                                                           'message': 'abc',
                                                           'submitbutton': '1'})
