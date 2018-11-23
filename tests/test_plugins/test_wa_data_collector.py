import os
import io
import gzip
import configparser
from unittest import mock

import pytest
import xmltodict
import networkx as nx

from meguca.plugins.src import wa_data_collector


@pytest.fixture(scope='module')
def prep_config():
    config = configparser.ConfigParser()
    config['Auth'] = {'useragent': ''}
    config['Region'] = {'name': 'region'}
    config['DataDump'] = {'filepath': 'meguca/nations.xml.gz'}

    wa_data_collector.WADataCollector.plg_config = config


@pytest.fixture
def mock_dump():
    dump = {'NATIONS': {'NATION': [{'NAME': 'nation1', 'REGION': 'region',
                              'UNSTATUS': 'WA Member', 'ENDORSEMENTS': 'nation2,nation3'},
                              {'NAME': 'nation2', 'REGION': 'region',
                              'UNSTATUS': 'WA Member', 'ENDORSEMENTS': 'nation1'},
                              {'NAME': 'nation3', 'REGION': 'region',
                              'UNSTATUS': 'WA Member', 'ENDORSEMENTS': ''}]}
                  }

    return io.StringIO(xmltodict.unparse(dump))


class TestLoadDump():
    def test_FileNotFoundError_when_load_dump(self):
        with pytest.raises(FileNotFoundError):
            wa_data_collector.load_dump('')


class TestAddEndo():
    def test_add_one_endo_with_both_nations_in_same_region(self):
        nations = nx.DiGraph()

        wa_data_collector.add_endo('a', 'b', nations, set(['a', 'b']))

        assert list(nations.edges) == [('a', 'b')]

    def test_add_one_endo_with_sender_not_in_same_region(self):
        nations = nx.DiGraph()

        wa_data_collector.add_endo('a', 'b', nations, set(['b']))

        assert 'a' not in nations


class TestGetEligibleNations():
    def test_run_with_datadump_xml(self, mock_dump):
        assert "nation1" in wa_data_collector.get_eligible_nations(mock_dump, 'region')


class TestLoadDataFromDump():
    def test_run_with_datadump_xml(self, mock_dump):
        nations = nx.DiGraph()
        eligible_nations = set(['nation1', 'nation2', 'nation3'])

        wa_data_collector.load_data_from_dump(nations, mock_dump, eligible_nations, 'region')

        assert ('nation1', 'nation2') in nations.edges


class TestLoadDataFromAPI():
    def test_add_endorsement(self):
        events = [{'TEXT': "@@nation1@@ endorsed @@nation2@@."}]
        nations = nx.DiGraph()

        wa_data_collector.load_data_from_api(events, nations)

        assert ('nation1', 'nation2') in nations.edges

    def test_remove_endorsement(self):
        events = [{'TEXT': "@@nation1@@ withdrew its endorsement from @@nation2@@."}]
        nations = nx.DiGraph([('nation1', 'nation2')])

        wa_data_collector.load_data_from_api(events, nations)

        assert ('nation1', 'nation2') not in nations.edges

    def test_new_wa_admission(self):
        events = [{'TEXT': "@@nation1@@ was admitted to the World Assembly."}]
        nations = nx.DiGraph()

        wa_data_collector.load_data_from_api(events, nations)

        assert 'nation1' in nations


class TestWADataCollector():
    @pytest.fixture(scope='class')
    def prep_dumpfile(self):
        with gzip.open('meguca/nations.xml.gz', 'wb') as f:
            f.write(mock_dump().read().encode())

        yield 0

        os.remove('meguca/nations.xml.gz')

    def test_prime_run_with_dump(self, prep_dumpfile, prep_config):
        ins = wa_data_collector.WADataCollector()

        assert ('nation1', 'nation2') in ins.prime_run()['wa_nations'].edges

    def test_run_with_mock_events(self, prep_dumpfile, prep_config):
        events = {'HAPPENINGS': {'EVENT': [
                        {'TEXT': '@@nation1@@ withdrew its endorsement from @@nation3@@.',
                         'TIMESTAMP': '2'},
                        {'TEXT': '@@nation1@@ endorsed @@nation2@@.',
                         'TIMESTAMP': '1'},
                        {'TEXT': '@@nation1@@ was admitted to the World Assembly.',
                         'TIMESTAMP': '0'}
                        ]}}


        ins = wa_data_collector.WADataCollector()
        ns_api = mock.Mock(get_world=mock.Mock(return_value=events))
        nations = nx.DiGraph([('nation1', 'nation3')])

        ins.run(data={'wa_nations': nations}, ns_api=ns_api)

        assert ('nation1', 'nation2') in nations.edges
        assert ('nation1', 'nation3') not in nations.edges
        assert ins.last_evt_time == '2'




