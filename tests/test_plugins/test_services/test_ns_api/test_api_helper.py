import pytest

from meguca.plugins.services.ns_api import api_helper

API_URL_BEGINNING = "https://www.nationstates.net/cgi-bin/api.cgi?"
API_PARAM_DELIMITER = ";"
API_PARAM_VALUE_DELIMITER = "+"

class TestURLConstructor():
    def test_multi_params_one_val(self):
        params = {'nation': 'test', 'q': 'test'}
        result = api_helper.construct_url(params,
                                          API_URL_BEGINNING,
                                          API_PARAM_DELIMITER,
                                          API_PARAM_VALUE_DELIMITER)

        assert result == "https://www.nationstates.net/cgi-bin/api.cgi?nation=test;q=test;"

    def test_multi_params_multi_vals(self):
        params = {'nation': 'test', 'q': ['test1', 'test2']}
        result = api_helper.construct_url(params,
                                          API_URL_BEGINNING,
                                          API_PARAM_DELIMITER,
                                          API_PARAM_VALUE_DELIMITER)

        assert result == "https://www.nationstates.net/cgi-bin/api.cgi?nation=test;q=test1+test2;"