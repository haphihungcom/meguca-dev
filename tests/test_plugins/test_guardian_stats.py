from unittest import mock

from meguca.plugins.src import guardian_stats


def mock_get_nation(nation, shard):
    if nation == 'guard 1':
        endorsees = 'nation1,nation2'
    elif nation == 'guard 2':
        endorsees = 'nation1,nation2,nation3'
    elif nation == 'guard 3':
        endorsees = 'nation1,nation2,nation3,nation4'

    return {'ENDORSEMENTS': endorsees}


class TestGuardianStats():
    def test(self):
        ins = guardian_stats.GuardianStats()
        ins.plg_config = {'criteria': {'required_to_endorse_nations': ['Guard_1', 'Guard_2', 'Guard_3']}}
        ns_api = mock.Mock(get_nation=mock.Mock(side_effect=mock_get_nation))

        result = ins.run(ns_api=ns_api)

        assert 'nation1' in result['guardians'] and 'nation2' in result['guardians']
