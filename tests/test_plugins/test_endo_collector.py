import os
import io
import gzip
from unittest import mock

import pytest
import xmltodict
import networkx as nx

from meguca.plugins.src.endo_collector import endo_collector
from meguca.plugins.src.endo_collector import exceptions


@pytest.fixture(scope='module')
def prep_config():
    plg_config = {'data_dump': {'path': 'meguca/nations.xml.gz'},
                  'precision': {'precision_mode': False}}
    endo_collector.EndoDataCollector.plg_config = plg_config

    meguca_config = {'general': {'region': 'region'}}

    return {'meguca': meguca_config}


def create_mock_dump():
    dump = {'NATIONS': {'NATION': [{'NAME': 'nation1', 'REGION': 'region',
                                    'UNSTATUS': 'WA Member', 'ENDORSEMENTS': 'nation2,nation3'},
                                   {'NAME': 'nation2', 'REGION': 'region',
                                    'UNSTATUS': 'WA Member', 'ENDORSEMENTS': 'nation1'},
                                   {'NAME': 'nation3', 'REGION': 'region',
                                    'UNSTATUS': 'WA Member', 'ENDORSEMENTS': ''}]}
           }

    return io.StringIO(xmltodict.unparse(dump))


@pytest.fixture
def mock_dump():
    return create_mock_dump()


class TestLoadDump():
    def test_FileNotFoundError_when_load_dump(self):
        with pytest.raises(exceptions.EndoCollectorError):
            endo_collector.load_dump('')


class TestAddEndo():
    def test_add_one_endo_with_both_nations_in_same_region(self):
        endos = nx.DiGraph()

        endo_collector.add_endo('a', 'b', endos, set(['a', 'b']))

        assert list(endos.edges) == [('a', 'b')]

    def test_add_one_endo_with_sender_not_in_same_region(self):
        endos = nx.DiGraph()

        endo_collector.add_endo('a', 'b', endos, set(['b']))

        assert 'a' not in endos


class TestGetEligibleNations():
    def test_run_with_datadump_xml(self, mock_dump):
        assert "nation1" in endo_collector.get_eligible_nations(mock_dump, 'region')


class TestLoadDataFromDump():
    def test_run_with_datadump_xml(self, mock_dump):
        endos = nx.DiGraph()
        eligible_nations = set(['nation1', 'nation2', 'nation3'])

        endo_collector.load_data_from_dump(endos, mock_dump, eligible_nations)

        assert ('nation1', 'nation2') in endos.edges


class TestLoadDataFromAPI():
    def test_add_endorsement(self):
        events = [{'TEXT': "@@nation1@@ endorsed @@nation2@@."}]
        endos = nx.DiGraph()

        endo_collector.load_data_from_api(events, endos)

        assert ('nation1', 'nation2') in endos.edges

    def test_remove_endorsement(self):
        events = [{'TEXT': "@@nation1@@ withdrew its endorsement from @@nation2@@."}]
        endos = nx.DiGraph([('nation1', 'nation2')])

        endo_collector.load_data_from_api(events, endos)

        assert ('nation1', 'nation2') not in endos.edges

    def test_new_wa_admission(self):
        events = [{'TEXT': "@@nation1@@ was admitted to the World Assembly."}]
        endos = nx.DiGraph()

        endo_collector.load_data_from_api(events, endos)

        assert 'nation1' in endos

    def test_illegal_endorsements_with_precision_mode(self):
        events = [{'TEXT': "@@nation1@@ withdrew its endorsement from @@nation2@@."}]
        endos = nx.DiGraph()

        with pytest.raises(exceptions.IllegalEndorsement):
            endo_collector.load_data_from_api(events, endos, precision_mode=True)

    def test_illegal_endorsements_with_no_precision_mode(self):
        events = [{'TEXT': "@@nation1@@ withdrew its endorsement from @@nation2@@."}]
        endos = nx.DiGraph()

        endo_collector.load_data_from_api(events, endos, precision_mode=False)

        assert True


class TestEndoDataCollector():
    @pytest.fixture(scope='class')
    def prep_dumpfile(self):
        with gzip.open('meguca/nations.xml.gz', 'wb') as f:
            f.write(create_mock_dump().read().encode())

        yield 0

        os.remove('meguca/nations.xml.gz')

    def test_prepare_with_dump(self, prep_dumpfile, prep_config):
        ins = endo_collector.EndoDataCollector()

        assert ('nation1', 'nation2') in ins.prepare(config=prep_config)['endos'].edges

    def test_run_with_mock_events(self, prep_dumpfile, prep_config):
        events = {'HAPPENINGS': {'EVENT': [
                        {'TEXT': '@@nation1@@ withdrew its endorsement from @@nation3@@.',
                         'TIMESTAMP': '2'},
                        {'TEXT': '@@nation1@@ endorsed @@nation2@@.',
                         'TIMESTAMP': '1'},
                        {'TEXT': '@@nation1@@ was admitted to the World Assembly.',
                         'TIMESTAMP': '0'}
                        ]}}


        ins = endo_collector.EndoDataCollector()
        ns_api = mock.Mock(get_world=mock.Mock(return_value=events))
        endos = nx.DiGraph([('nation1', 'nation3')])

        ins.run(data={'endos': endos}, ns_api=ns_api, config=prep_config)

        assert ('nation1', 'nation2') in endos.edges
        assert ('nation1', 'nation3') not in endos.edges
        assert ins.last_evt_time == '2'
