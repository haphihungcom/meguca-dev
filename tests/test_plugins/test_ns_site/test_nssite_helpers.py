from unittest import mock

import pytest

from meguca.plugins.src.ns_site import helpers
from meguca.plugins.src.ns_site import exceptions


class TestHandleErrors():
    def test_raise_no_exception(self):
        resp = mock.Mock(status_code=200, text='')

        helpers.handle_errors(resp)

    def test_raise_exception_non_200_http_status_code(self):
        resp = mock.Mock(status_code=404, text='')

        with pytest.raises(exceptions.NSSiteHTTPError):
            helpers.handle_errors(resp)

    def test_raise_exception_type_1_security_error(self):
        html = '<p class="error">This request failed a security check. Please try again.</p>'
        resp = mock.Mock(status_code=200, text=html)

        with pytest.raises(exceptions.NSSiteSecurityError):
            helpers.handle_errors(resp)

    def test_raise_exception_type_2_security_error(self):
        html = '<p class="error">Failed security check.</p>'
        resp = mock.Mock(status_code=200, text=html)

        with pytest.raises(exceptions.NSSiteSecurityError):
            helpers.handle_errors(resp)

    def test_raise_exception_page_not_found(self):
        html = '<p class="error">The requested page does not exist.</p>'
        resp = mock.Mock(status_code=200, text=html)

        with pytest.raises(exceptions.NSSiteNotFound):
            helpers.handle_errors(resp)


class TestGetLocalId():
    def test_get_localid_from_html_text(self):
        html = '<input type="hidden" name="localid" value="123456">'

        assert helpers.get_localid(html) == '123456'
