import re

import pytest
import requests

from meguca import ns_api

TEST_USER_AGENT = "Unit tests of Meguca | NS API Wrapper component"

class TestNSApi():
    def test_get_nation_one_shard(self):
        api = ns_api.NSApi(TEST_USER_AGENT)
        result = api.get_nation('testlandia', shards='name')

        assert result['NAME'] == "Testlandia"

    def test_get_nation_multi_shards(self):
        api = ns_api.NSApi(TEST_USER_AGENT)
        result = api.get_nation('testlandia', shards=['name', 'region'])

        assert result['NAME'] == "Testlandia"
        assert result['REGION'] == 'Testregionia'

    def test_get_nation_census_shard_multi_params(self):
        api = ns_api.NSApi(TEST_USER_AGENT)
        result = api.get_nation('testlandia',
                                shards='census',
                                shard_params={'mode': 'score',
                                              'scale': '1'})

        assert re.match('\d+',result['CENSUS']['SCALE']['SCORE']) is not None

    def test_get_nation_census_shard_multi_scales_multi_params_multi_modes(self):
        api = ns_api.NSApi(TEST_USER_AGENT)
        result = api.get_nation('testlandia',
                                shards='census',
                                shard_params={'mode': ['score', 'rank'],
                                              'scale': ['1', '2']})

        assert re.match('\d+',result['CENSUS']['SCALE'][0]['SCORE']) is not None
        assert re.match('\d+',result['CENSUS']['SCALE'][1]['SCORE']) is not None

    def test_get_nation_multi_shards_multi_scales_multi_params_multi_modes(self):
        api = ns_api.NSApi(TEST_USER_AGENT)
        result = api.get_nation('testlandia',
                                shards=['name', 'census'],
                                shard_params={'mode': ['score', 'rank'],
                                              'scale': ['1', '2']})

        assert result['NAME'] == 'Testlandia'
        assert re.match('\d+',result['CENSUS']['SCALE'][0]['SCORE']) is not None
        assert re.match('\d+',result['CENSUS']['SCALE'][0]['RANK']) is not None
        assert re.match('\d+',result['CENSUS']['SCALE'][1]['SCORE']) is not None
        assert re.match('\d+',result['CENSUS']['SCALE'][1]['RANK']) is not None

    def test_get_region_one_shard(self):
        api = ns_api.NSApi(TEST_USER_AGENT)
        result = api.get_region('testregionia', shards='name')

        assert result['NAME'] == "Testregionia"

    def test_get_world_one_shard(self):
        api = ns_api.NSApi(TEST_USER_AGENT)
        result = api.get_world(shards='regions')

        assert "Testregionia" in result['REGIONS']

    def test_get_non_existent_nation(self):
        api = ns_api.NSApi(TEST_USER_AGENT)

        with pytest.raises(Exception):
            api.get_nation('a', shards='')

    def test_get_world_no_shard(self):
        api = ns_api.NSApi(TEST_USER_AGENT)

        with pytest.raises(Exception):
            api.get_world(shards='')

    def test_api_ratelimit_exceeded(self):
        # Fake rate limit. For obvious reasons,
        # testing using real limit would be difficult
        ns_api.RATE_LIMIT = 1
        api = ns_api.NSApi(TEST_USER_AGENT)

        with pytest.raises(Exception):
            for i in range(0,3):
                api.get_world(shards='lasteventid')


class TestNSApiAuth():
    def test_password_auth(self):
        api = ns_api.NSApi(TEST_USER_AGENT, password='12345678')

        assert api.req_headers['X-Password'] == '12345678'

    def test_pin_auth(self):
        api = ns_api.NSApi(TEST_USER_AGENT, password='12345678')
        resp_with_pin = requests.Response()
        resp_with_pin.headers['X-Pin'] = '1'
        api.set_pin(resp_with_pin)

        assert api.req_headers['X-Pin'] == '1' and 'X-Password' not in api.req_headers

    def test_forbidden(self):
        ns_api.API_URL_BEGINNING = 'https://httpstat.us/403'
        api = ns_api.NSApi(TEST_USER_AGENT, password='12345678')

        with pytest.raises(Exception):
            api.get_nation('', shards='')



