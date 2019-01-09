import configparser
from unittest import mock

import pytest

from meguca.plugins.src.services.ns_site import ns_site
from meguca.plugins.src.services.ns_site import exceptions


class TestNSSiteHandleErrors():
    def test_raise_exception_non_200_http_status_code(self):
        ins = ns_site.NSSite('', '')
        resp = mock.Mock(status_code=404, text='')

        with pytest.raises(exceptions.NSSiteHTTPError):
            ins.handle_errors(resp)

    def test_raise_exception_type_1_security_error(self):
        ins = ns_site.NSSite('', '')
        html = '<p class="error">This request failed a security check. Please try again.</p>'

        resp = mock.Mock(status_code=200, text=html)

        with pytest.raises(exceptions.NSSiteSecurityError):
            ins.handle_errors(resp)

    def test_raise_exception_type_2_security_error(self):
        ins = ns_site.NSSite('', '')
        html = '<p class="error">Failed security check.</p>'

        resp = mock.Mock(status_code=200, text=html)

        with pytest.raises(exceptions.NSSiteSecurityError):
            ins.handle_errors(resp)

    def test_raise_exception_page_not_found(self):
        ins = ns_site.NSSite('', '')
        html = '<p class="error">The requested page does not exist.</p>'

        resp = mock.Mock(status_code=200, text=html)

        with pytest.raises(exceptions.NSSiteNotFound):
            ins.handle_errors(resp)


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
    def test_init_get_pin_from_ns_api(self):
        plg = ns_site.NSSitePlugin()
        config = configparser.ConfigParser()
        config['Auth'] = {'useragent': 'Test'}
        ns_api = mock.Mock(session=mock.Mock(headers={'X-Pin': '12345'}))

        ins = plg.get(ns_api=ns_api, config={'Meguca': config})

        assert ins.session.cookies['pin'] == '12345'

    def test_send_dispatch_update_request(self):
        plg = ns_site.NSSitePlugin()
        config = configparser.ConfigParser()
        config['Auth'] = {'useragent': 'Test'}
        ns_api = mock.Mock(session=mock.Mock(headers={'X-Pin': '12345'}))
        ins = plg.get(ns_api=ns_api, config={'Meguca': config})

        with mock.patch('requests.Session.get',
                        return_value=mock.Mock(status_code=200,
                                               text='<input type="hidden" name="localid" value="li42rYLF326ZS">')):
            ins.set_localid()

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



