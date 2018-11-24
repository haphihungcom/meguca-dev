import gzip
import xml.etree.cElementTree as ET

import networkx as nx

from meguca import plugin_categories
from meguca import utils


def load_dump(dump_path):
    """Load NS data dump file."""

    try:
        dump = gzip.open(dump_path)
    except FileNotFoundError as e:
        raise FileNotFoundError('Could not find data dump file.') from e

    return dump


def add_endo(endo_sender, endo_receiver, endos, eligible_nations):
    if endo_sender in eligible_nations:
        endos.add_edge(endo_sender, endo_receiver)


def get_eligible_nations(dump, region_name):
    """Build a set of eligible nations (in WA and configured region)
    to remove a bug."""

    eligible_nations = set()

    for evt, elem in ET.iterparse(dump):
        if elem.tag == 'NATION':
            if (elem.find('REGION').text == region_name
                and elem.find('UNSTATUS').text.find('WA') != -1):

                nation_name = utils.canonical(elem.find('NAME').text)
                eligible_nations.add(nation_name)

            elem.clear()

    return eligible_nations


def load_data_from_dump(endos, dump, eligible_nations, region_name):
    """Build nation graph with data from NS data dump."""

    is_in_region = False
    for evt, elem in ET.iterparse(dump):
        if elem.tag == 'NATION':
            nation_name = utils.canonical(elem.find('NAME').text)

            if nation_name in eligible_nations:
                is_in_region = True
                endos_text = utils.canonical(elem.find('ENDORSEMENTS').text)

                if endos_text is None:
                    endos.add_node(nation_name)
                elif "," not in endos_text:
                    add_endo(endos_text, nation_name, endos, eligible_nations)
                elif "," in endos_text:
                    for endo in endos_text.split(","):
                        add_endo(endo, nation_name, endos, eligible_nations)

            elif is_in_region:
                break

            elem.clear()


def load_data_from_api(events, endos):
    for event in reversed(events):
        event_text = utils.canonical(event['TEXT'].replace('@@', '')[:-1])

        if "endorsed" in event_text:
            endo = event_text.split(" endorsed ")
            endos.add_edge(endo[0], endo[1])
        elif "withdrew its endorsement from" in event_text:
            endo = event_text.split(" withdrew its endorsement from ")
            endos.remove_edge(endo[0], endo[1])
        elif "was admitted to the world assembly" in event_text:
            nation = event_text.split(" was admitted to the world assembly")[0]
            endos.add_node(nation)


class EndoDataCollector(plugin_categories.Collector):
    last_evt_time = ''

    def run(self, data, ns_api, config):
        shard_params = {'view': 'region.{}'.format(config['Meguca']['General']['regionname']),
                        'filter': ['endo', 'member'],
                        'sincetime': self.last_evt_time}
        events = ns_api.get_world('happenings', shard_params=shard_params)['HAPPENINGS']['EVENT']
        self.last_evt_time = events[0]['TIMESTAMP']

        load_data_from_api(events, data['endos'])

    def prime_run(self, config):
        # A directional graph to store nations and their endorsements
        endos = nx.DiGraph()
        dump = load_dump(self.plg_config['DataDump']['filepath'])

        eligible_nations = get_eligible_nations(dump, config['Meguca']['General']['regionname'])
        dump.seek(0)
        load_data_from_dump(endos, dump, eligible_nations, config['Meguca']['General']['regionname'])

        return {'endos': endos}