import os
import logging
import json
from unittest import mock

import pytest
import toml

from meguca.plugins.src.dispatch_updater import dispatch_renderer
from meguca.plugins.src.dispatch_updater import dispatch_updater


class TestDispatchUpdater():
    @pytest.mark.use_fixtures('mock_templates', 'toml_files')
    @pytest.fixture
    def setup_plugin_and_templates(self, mock_templates, toml_files):
        templates = {'tests/template_1.txt': '{% for i in j %}{{ i }}{% endfor %}',
                     'tests/template_2.txt': '{{ k }}',
                     'tests/template_3.txt': '{{ s }}'}

        mock_templates(templates)

        ins = dispatch_updater.DispatchUpdater()
        data = {'j': [1, 2, 3]}
        mock_ns_site = mock.Mock(execute=mock.Mock(return_value=('<p class="info"> ABCD <a href="/page=dispatch/'
                                                                 'id=1234567">CDSE</a></p>')))

        config = {'general': {'template_dir_path': 'tests',
                              'dispatch_config_path': 'tests/dispatches.toml',
                              'filters_path': 'tests/resources/filters.py',
                              'custom_vars_path': '',
                              'template_file_ext': 'txt',
                              'bb_path': 'tests/resources/bb_formatters.toml',
                              'id_store_path': 'tests/id_store.json'},
                  'dry_run': {'enabled': False, 'dispatches': []}}

        dispatch_config = {'template_1': {'id': 12345, 'title': 'Example 1',
                                          'category': 123, 'sub_category': 456},
                           'template_2': {'id': 67890, 'title': 'Example 2',
                                          'category': 789, 'sub_category': 123},
                            'template_3': {'title': 'Example 3', 'category': 789,
                                           'sub_category': 123}}
        toml_files({'tests/dispatches.toml': dispatch_config})

        ins.plg_config = config
        ins.prepare(mock_ns_site, data)

        yield ins

        os.remove('tests/id_store.json')

    @mock.patch('meguca.plugins.src.dispatch_updater.utils.get_new_dispatch_id', return_value=1234567)
    def test_add_dispatch_id(self, mock_get_new_dispatch_id):
        ins = dispatch_updater.DispatchUpdater()
        ins.id_store = {}

        ins.add_dispatch_id('<p>abcd</p>', 'test')

        assert ins.id_store['test'] == 1234567

    def test_upload_dispatch_with_id(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.ns_site = mock.Mock(execute=mock.Mock())
        template_info = {'title': 'Test', 'category': 123,
                         'sub_category': 456}

        ins.upload_dispatch(template_info, 'abc', '12345')

        ins.ns_site.execute.assert_called_with('lodge_dispatch',
                                               {'edit': '12345',
                                                'category': '123',
                                                'subcategory-123': '456',
                                                'dname': 'Test',
                                                'message': 'abc',
                                                'submitbutton': '1'})

    def test_upload_dispatch_with_no_id(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.ns_site = mock.Mock(execute=mock.Mock())
        template_info = {'title': 'Test', 'category': 123,
                         'sub_category': 456}

        ins.upload_dispatch(template_info, 'abc')

        ins.ns_site.execute.assert_called_with('lodge_dispatch',
                                               {'edit': None,
                                                'category': '123',
                                                'subcategory-123': '456',
                                                'dname': 'Test',
                                                'message': 'abc',
                                                'submitbutton': '1'})

    def test_update_dispatch_with_no_id(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.renderer = mock.Mock(render=mock.Mock(return_value='abc'))
        ins.id_store = {}
        ins.upload_dispatch = mock.Mock(return_value='<p>Test</p>')
        ins.add_dispatch_id = mock.Mock()
        template_info = {'title': 'Test', 'category': 123,
                         'sub_category': 456}

        ins.update_dispatch('test', template_info)

        ins.upload_dispatch.assert_called_with(template_info, 'abc')
        ins.add_dispatch_id.assert_called_with('<p>Test</p>', 'test')

    def test_update_dispatch_with_id_in_store(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.renderer = mock.Mock(render=mock.Mock(return_value='abc'))
        ins.id_store = {'test': 1234567}
        ins.upload_dispatch = mock.Mock(return_value='<p>Test</p>')
        ins.add_dispatch_id = mock.Mock()
        template_info = {'title': 'Test', 'category': 123,
                         'sub_category': 456}

        ins.update_dispatch('test', template_info)

        ins.upload_dispatch.assert_called_with({'title': 'Test',
                                                'category': 123,
                                                'sub_category': 456},
                                                'abc', '1234567')
        ins.add_dispatch_id.assert_not_called()

    def test_update_all_dispatches_with_dispatches(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.dispatches = {'a': '1', 'b': '2'}
        ins.update_dispatch = mock.Mock()

        ins.update_all_dispatches()

        expected_calls = [mock.call('a', '1'), mock.call('b', '2')]
        ins.update_dispatch.assert_has_calls(expected_calls)

    def test_update_all_dispatches_with_no_dispatches(self, caplog):
        """If no dispatch is configured, should issue a log warning.
        """

        caplog.set_level(logging.WARNING)

        ins = dispatch_updater.DispatchUpdater()
        ins.dispatches = {}
        ins.update_dispatch = mock.Mock()

        ins.update_all_dispatches()

        for record in caplog.records:
            assert record.levelname == 'WARNING'

    def test_dry_run_multiple_dispatches(self, setup_plugin_and_templates):
        ins = setup_plugin_and_templates
        ins.plg_config['dry_run'] = {'enabled': True,
                                     'dispatches': ['template_1', 'template_3']}
        ins.data = {'k': 5, 's': 10}

        ins.dry_run()

        expected_calls = [mock.call('lodge_dispatch',
                                    {'edit': '12345',
                                     'category': '123',
                                     'subcategory-123': '456',
                                     'dname': 'Example 1',
                                     'message': '123',
                                     'submitbutton': '1'}),
                          mock.call('lodge_dispatch',
                                    {'edit': None,
                                     'category': '789',
                                     'subcategory-789': '123',
                                     'dname': 'Example 3',
                                     'message': '10',
                                     'submitbutton': '1'})]
        ins.ns_site.execute.assert_has_calls(expected_calls)

        with open('tests/id_store.json') as f:
            assert json.load(f) == {'template_1': 12345, 'template_2': 67890,
                                    'template_3': 1234567}

    def test_dry_run_multiple_dispatches_with_no_dispatches_configured(self, setup_plugin_and_templates):
        """If dispatches config is empty, should dry run all dispatches.
        """

        ins = setup_plugin_and_templates
        ins.plg_config['dry_run'] = {'enabled': True,
                                     'dispatches': []}
        ins.data = {'k': 5, 's': 10}

        ins.dry_run()

        expected_calls = [mock.call('lodge_dispatch',
                                    {'edit': '12345',
                                     'category': '123',
                                     'subcategory-123': '456',
                                     'dname': 'Example 1',
                                     'message': '123',
                                     'submitbutton': '1'}),
                          mock.call('lodge_dispatch',
                                    {'edit': '67890',
                                     'category': '789',
                                     'subcategory-789': '123',
                                     'dname': 'Example 2',
                                     'message': '5',
                                     'submitbutton': '1'}),
                          mock.call('lodge_dispatch',
                                    {'edit': None,
                                     'category': '789',
                                     'subcategory-789': '123',
                                     'dname': 'Example 3',
                                     'message': '10',
                                     'submitbutton': '1'})]
        ins.ns_site.execute.assert_has_calls(expected_calls)

        with open('tests/id_store.json') as f:
            assert json.load(f) == {'template_1': 12345, 'template_2': 67890,
                                    'template_3': 1234567}

    def test_run_multiple_dispatches(self, setup_plugin_and_templates):
        ins = setup_plugin_and_templates
        ins.data = {'k': 5, 's': 10}

        ins.run()

        expected_calls = [mock.call('lodge_dispatch',
                                    {'edit': '12345',
                                     'category': '123',
                                     'subcategory-123': '456',
                                     'dname': 'Example 1',
                                     'message': '123',
                                     'submitbutton': '1'}),
                          mock.call('lodge_dispatch',
                                    {'edit': '67890',
                                     'category': '789',
                                     'subcategory-789': '123',
                                     'dname': 'Example 2',
                                     'message': '5',
                                     'submitbutton': '1'}),
                          mock.call('lodge_dispatch',
                                    {'edit': None,
                                     'category': '789',
                                     'subcategory-789': '123',
                                     'dname': 'Example 3',
                                     'message': '10',
                                     'submitbutton': '1'})]
        ins.ns_site.execute.assert_has_calls(expected_calls)

        with open('tests/id_store.json') as f:
            assert json.load(f) == {'template_1': 12345, 'template_2': 67890,
                                    'template_3': 1234567}
