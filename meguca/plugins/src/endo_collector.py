"""Collect endorsement data from the API and data dump.
"""


import gzip
import xml.etree.cElementTree as ET

import networkx as nx

from meguca import plugin_categories
from meguca import utils


def load_dump(dump_path):
    """Load NationStates data dump file.

    Args:
        dump_path (str): Path to data dump file.

    Raises:
        FileNotFoundError: Raises if cannot find data dump file.

    Returns:
        file object: Data dump file object.
    """


    try:
        dump = gzip.open(dump_path)
    except FileNotFoundError as e:
        raise FileNotFoundError('Could not find data dump file.') from e

    return dump


def add_endo(endo_sender, endo_receiver, endos, eligible_nations):
    """Add endorsements to graph.

    Args:
        endo_sender (str): Endorsement-sending nation.
        endo_receiver (str): Endorsement-receiving nation.
        endos (networkx.DiGraph): Endorsement graph.
        eligible_nations (set): Used to confirm an endorsement is valid.
    """

    if endo_sender in eligible_nations:
        endos.add_edge(endo_sender, endo_receiver)


def get_eligible_nations(dump, region_name):
    """Get eligible nations to confirm validity of endorsements.
    Read NationStates's data dump endorsement issue for the rationale
    behind this.

    Args:
        dump (file object): Data dump file.
        region_name (str): Region.

    Returns:
        set: Eligible nations.
    """


    eligible_nations = set()

    for evt, elem in ET.iterparse(dump):
        if elem.tag == 'NATION':
            if (elem.find('REGION').text == region_name and
                elem.find('UNSTATUS').text.find('WA') != -1):

                nation_name = utils.canonical(elem.find('NAME').text)
                eligible_nations.add(nation_name)

            elem.clear()

    return eligible_nations


def load_data_from_dump(endos, dump, eligible_nations):
    """Build the endorsement graph using data from the data dump.

    Args:
        endos (networkx.DiGraph): Endorsement graph.
        dump (file object): Data dump file.
        eligible_nations (set): Used to confirm an endorsement is valid.
    """


    is_in_region = False
    for evt, elem in ET.iterparse(dump):
        if elem.tag == 'NATION':
            nation_name = utils.canonical(elem.find('NAME').text)

            if nation_name in eligible_nations:
                is_in_region = True

                endos_text = elem.find('ENDORSEMENTS').text
                if endos_text is not None:
                    endos_text = utils.canonical(endos_text)

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
    """Update the endorsement graph with data from the happenings API.

    Args:
        events (list): Relevant happenings.
        endos (networkx.DiGraph): Endorsement graph.
    """

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
        """Load new happenings from the API and update the endorsement graph."""
        shard_params = {'view': 'region.{}'.format(config['Meguca']['General']['Region']),
                        'filter': ['endo', 'member'],
                        'sincetime': self.last_evt_time}
        events = ns_api.get_world('happenings', shard_params=shard_params)['HAPPENINGS']['EVENT']
        self.last_evt_time = events[0]['TIMESTAMP']

        load_data_from_api(events, data['endos'])

    def prime_run(self, config):
        """Make an initial endorsement graph using the data dump."""

        # A directional graph to store endorsement data.
        endos = nx.DiGraph()
        dump = load_dump(self.plg_config['DataDump']['FilePath'])

        eligible_nations = get_eligible_nations(dump, config['Meguca']['General']['Region'])
        dump.seek(0)
        load_data_from_dump(endos, dump, eligible_nations)

        return {'endos': endos}
