import os
import json
import toml
import logging
from unittest import mock

import pytest

from meguca.plugins.src.dispatch_updater import utils


class TestIDStore():
    @pytest.fixture
    def setup_test_file(self):
        with open('test.json', 'w') as f:
            json.dump({'Test': 1}, f)

        yield

        os.remove('test.json')

    def test_init_load_id_store_from_json_when_file_not_exist(self, setup_test_file):
        os.remove('test.json')
        ins = utils.IDStore('test.json')

        ins.load_from_json()

        assert os.path.isfile('test.json')
        assert ins._store == {}

    def test_init_load_id_store_when_file_already_exists(self, setup_test_file):
        ins = utils.IDStore('test.json')

        ins.load_from_json()

        assert ins._store == {'Test': 1}

    def test_load_id_store_from_dispatches(self):
        ins = utils.IDStore('test.json')
        ins._store = {'Test1': 1}

        ins.load_from_dispatch_config({'dis1': {'id': 2, 'title': 'a'},
                                       'dis2': {'title': 'a'}})

        assert ins._store == {'Test1': 1, 'dis1': 2}

    def test_getitem(self):
        ins = utils.IDStore('')
        ins._store = {'Test': 1}

        assert ins['Test'] == 1

    def test_setitem(self):
        ins = utils.IDStore('')
        ins._store = {'Test': 1}

        ins['Test1'] = 2

        assert ins._store == {'Test': 1, 'Test1': 2}

    def test_contains(self):
        ins = utils.IDStore('')
        ins._store = {'Test': 1}

        assert 'Test' in ins

    def test_add_id_from_html(self):
        ins = utils.IDStore('')
        html = '<p class="info"> ABCD <a href="/page=dispatch/id=1234567">CDSE</a></p>'

        ins.add_id_from_html('test', html)

        ins._store['test'] = 1234567

    @mock.patch('json.dump')
    def test_save_when_saved_is_true(self, mock_json_dump, setup_test_file):
        ins = utils.IDStore('test.json')
        ins.saved = True

        ins.save()

        mock_json_dump.assert_not_called()

    @mock.patch('json.dump')
    def test_save_when_saved_is_false(self, mock_json_dump, setup_test_file):
        ins = utils.IDStore('test.json')
        ins.saved = False

        ins.save()

        mock_json_dump.assert_called_once()


class TestLoadDispatchConfig():
    @pytest.fixture
    def setup_test_file(self, scope='class'):
        with open('test1.toml', 'w') as f:
            toml.dump({'Test1': 'TestVal1'}, f)

        with open('test2.toml', 'w') as f:
            toml.dump({'Test2': 'TestVal2'}, f)

        yield

        os.remove('test1.toml')
        os.remove('test2.toml')

    def test_when_dispatch_config_path_is_str(self, setup_test_file):
        r = utils.load_dispatch_config('test1.toml')

        assert r == {'Test1': 'TestVal1'}

    def test_when_dispatch_config_path_is_list(self, setup_test_file):
        r = utils.load_dispatch_config(['test1.toml', 'test2.toml'])

        assert r == {'Test1': 'TestVal1', 'Test2': 'TestVal2'}
