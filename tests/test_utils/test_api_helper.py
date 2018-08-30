import pytest

from meguca.utils import api_helper

API_URL_BEGINNING = "https://www.nationstates.net/cgi-bin/api.cgi?"
API_PARAM_DELIMITER = ";"
API_PARAM_VALUE_DELIMITER = "+"

class TestURLConstructor():
    def test_nation_multi_params_multi_vals(self):
        params = {'nation': 'test nation',
                  'q': ['name', 'census'],
                  'mode': ['score', 'rank'],
                  'scale': ['12', '13']}
        result = api_helper.construct_url(params,
                                          API_URL_BEGINNING,
                                          API_PARAM_DELIMITER,
                                          API_PARAM_VALUE_DELIMITER)

        assert result == "https://www.nationstates.net/cgi-bin/api.cgi?nation=test nation;q=name+census;mode=score+rank;scale=12+13;"

    def test_empty_params(self):
        params = {'':''}
        result = api_helper.construct_url(params,
                                          API_URL_BEGINNING,
                                          API_PARAM_DELIMITER,
                                          API_PARAM_VALUE_DELIMITER)
        assert result == "https://www.nationstates.net/cgi-bin/api.cgi?"