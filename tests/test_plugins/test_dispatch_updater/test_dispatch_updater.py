import os
import logging
import json
from unittest import mock

import pytest
import toml

from meguca.plugins.src.dispatch_updater import dispatch_renderer
from meguca.plugins.src.dispatch_updater import dispatch_updater


class TestDispatchUploader():
    def test_post_dispatch_with_id(self):
        mock_renderer = mock.Mock()
        mock_ns_site = mock.Mock(execute=mock.Mock(return_value='test'))
        dispatch_config = {'title': 'Test', 'category': 123,
                           'sub_category': 456}
        ins = dispatch_updater.DispatchUploader(mock_renderer, mock_ns_site,
                                                {}, {})

        r = ins.post_dispatch(dispatch_config, 'abc', 1234567)

        mock_ns_site.execute.assert_called_with('lodge_dispatch',
                                               {'category': '123',
                                                'subcategory-123': '456',
                                                'dname': 'Test',
                                                'message': b'abc',
                                                'submitbutton': '1',
                                                'edit': '1234567',})
        assert r == 'test'

    def test_post_dispatch_with_no_id(self):
        mock_ns_site = mock.Mock(execute=mock.Mock(return_value='test'))
        dispatch_config = {'title': 'Test', 'category': 123,
                           'sub_category': 456}
        ins = dispatch_updater.DispatchUploader(mock.Mock(), mock_ns_site, {}, {})

        r = ins.post_dispatch(dispatch_config, 'abc')

        mock_ns_site.execute.assert_called_with('lodge_dispatch',
                                               {'category': '123',
                                                'subcategory-123': '456',
                                                'dname': 'Test',
                                                'message': b'abc',
                                                'submitbutton': '1'})
        assert r == 'test'

    def test_update_dispatch(self):
        mock_renderer = mock.Mock(render=mock.Mock(return_value='abcd'))
        id_store = {'test1': 1234567, 'test2': 8901234}
        dispatch_config = {'test1': {'title': 'Test', 'category': 123,
                                    'sub_category': 456},
                           'test2': {'title': 'Test', 'category': 123,
                                     'sub_category': 456}}
        ins = dispatch_updater.DispatchUploader(mock_renderer, mock.Mock(),
                                                id_store, dispatch_config)
        ins.post_dispatch = mock.Mock()

        ins.update_dispatch('test1')

        ins.post_dispatch.assert_called_with(dispatch_config['test1'],
                                             'abcd', 1234567)

    def test_create_dispatch(self):
        dispatch_config = {'test1': {'title': 'Test', 'category': 123,
                                    'sub_category': 456},
                           'test2': {'title': 'Test', 'category': 123,
                                     'sub_category': 456}}
        ins = dispatch_updater.DispatchUploader(mock.Mock(), mock.Mock(),
                                                {}, dispatch_config)
        ins.post_dispatch = mock.Mock()

        ins.create_dispatch('test1')

        ins.post_dispatch.assert_called_with(dispatch_config['test1'], '[reserved]')


class TestDispatchUpdater():
    def test_create_dispatches(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.uploader = mock.Mock(create_dispatch=mock.Mock(return_value='<p>test</p>'))
        ins.id_store = mock.Mock(add_id_from_html=mock.Mock(),
                                 __contains__=mock.Mock(return_value=False))

        ins.create_dispatches(['test1', 'test2'])

        ins.id_store.add_id_from_html.assert_called_with('test2', '<p>test</p>')

    def test_create_dispatches(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.uploader = mock.Mock(create_dispatch=mock.Mock(return_value='<p>test</p>'))
        def contains(name):
            if name == 'test1':
                return True
            elif name == 'test2':
                return False
        ins.id_store = mock.Mock(add_id_from_html=mock.Mock(),
                                 __contains__=mock.Mock(side_effect=contains))

        ins.create_dispatches(['test1', 'test2'])

        ins.id_store.add_id_from_html.assert_called_with('test2', '<p>test</p>')

    def test_update_dispatches(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.uploader = mock.Mock(update_dispatch=mock.Mock())

        ins.update_dispatches(['test1', 'test2'])

        ins.uploader.update_dispatch.assert_called_with('test2')

    def test_get_allowed_dispatches(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.blacklist = ['test3']
        ins.dispatch_config = {'test1': {}, 'test2': {}, 'test3': {}}

        r = ins.get_allowed_dispatches()
        assert r == ['test1', 'test2']


class TestDispatchUpdaterIntegration():
    @pytest.mark.use_fixtures('text_files', 'toml_files')
    @pytest.fixture
    def setup_plugin_and_templates(self, text_files, toml_files):
        templates = {'tests/template_1.txt': '{% for i in data_products.j %}{{ i }}{% endfor %}',
                     'tests/template_2.txt': '{{ ext_config.meguca.general.dummy }}',
                     'tests/template_3.txt': '{{ s }} {{ k }} {{ dispatch_info.template_2.id }}'}
        text_files(templates)

        data = {'j': [1, 2, 3]}
        config = {'meguca': {'general': {'dummy': 'testval'}},
                  'plg1': {'general': {'enable': 'testval'}}}

        custom_vars = {'k': 5, 's': 10}
        toml_files({'tests/custom_vars.toml': custom_vars})

        mock_ns_site = mock.Mock(execute=mock.Mock(return_value=('<p class="info"> ABCD <a href="/page=dispatch/'
                                                                 'id=1234567">CDSE</a></p>')))

        plg_config = {'general': {'dispatch_config_path': 'tests/dispatches.toml',
                                  'id_store_path': 'tests/id_store.json'},
                      'renderer': {'template': {'template_dir_path': 'tests',
                                                'filters_path': 'tests/resources/filters.py',
                                                'template_file_ext': 'txt'},
                                   'bbcode': {'simple_formatter_path': 'tests/resources/bb_simple_formatters.toml',
                                              'complex_formatter_path': 'tests/resources/bb_complex_formatters.py',
                                              'complex_formatter_config_path': 'tests/resources/bb_complex_formatter_config.toml'},
                                   'custom_vars_path': 'tests/custom_vars.toml'},
                      'dry_run': {'dispatches': ['template_1', 'template_3']}}


        dispatch_config = {'template_1': {'id': 12345, 'title': 'Example 1',
                                          'category': 123, 'sub_category': 456},
                           'template_2': {'id': 67890, 'title': 'Example 2',
                                          'category': 789, 'sub_category': 123},
                           'template_3': {'title': 'Example 3', 'category': 789,
                                          'sub_category': 123}}
        toml_files({'tests/dispatches.toml': dispatch_config})

        ins = dispatch_updater.DispatchUpdater()
        ins.plg_config = plg_config
        ins.prepare(mock_ns_site, config, data)

        yield ins

        os.remove('tests/id_store.json')
    def test_dry_run_multiple_dispatches(self, setup_plugin_and_templates):
        ins = setup_plugin_and_templates
        ins.plg_config['dry_run'] = {'dispatches': ['template_1', 'template_3']}

        ins.dry_run()

        expected_calls = [mock.call('lodge_dispatch',
                                    {'edit': '12345',
                                     'category': '123',
                                     'subcategory-123': '456',
                                     'dname': 'Example 1',
                                     'message': b'123',
                                     'submitbutton': '1'}),
                          mock.call('lodge_dispatch',
                                    {'edit': '1234567',
                                     'category': '789',
                                     'subcategory-789': '123',
                                     'dname': 'Example 3',
                                     'message': b'10 5 67890',
                                     'submitbutton': '1'})]
        ins.ns_site.execute.assert_has_calls(expected_calls)

        with open('tests/id_store.json') as f:
            assert json.load(f) == {'template_1': 12345, 'template_2': 67890,
                                    'template_3': 1234567}

    def test_dry_run_multiple_dispatches_with_no_dispatches_configured(self, setup_plugin_and_templates):
        """If dispatches config is empty, should dry run all dispatches.
        """

        ins = setup_plugin_and_templates
        ins.dry_run_dispatches = None

        ins.dry_run()

        expected_calls = [mock.call('lodge_dispatch',
                                    {'edit': '12345',
                                     'category': '123',
                                     'subcategory-123': '456',
                                     'dname': 'Example 1',
                                     'message': b'123',
                                     'submitbutton': '1'}),
                          mock.call('lodge_dispatch',
                                    {'edit': '67890',
                                     'category': '789',
                                     'subcategory-789': '123',
                                     'dname': 'Example 2',
                                     'message': b'testval',
                                     'submitbutton': '1'}),
                          mock.call('lodge_dispatch',
                                    {'edit': '1234567',
                                     'category': '789',
                                     'subcategory-789': '123',
                                     'dname': 'Example 3',
                                     'message': b'10 5 67890',
                                     'submitbutton': '1'})]
        ins.ns_site.execute.assert_has_calls(expected_calls)

        with open('tests/id_store.json') as f:
            assert json.load(f) == {'template_1': 12345, 'template_2': 67890,
                                    'template_3': 1234567}

    def test_run_multiple_dispatches(self, setup_plugin_and_templates):
        ins = setup_plugin_and_templates

        ins.run()

        expected_calls = [mock.call('lodge_dispatch',
                                    {'edit': '12345',
                                     'category': '123',
                                     'subcategory-123': '456',
                                     'dname': 'Example 1',
                                     'message': b'123',
                                     'submitbutton': '1'}),
                          mock.call('lodge_dispatch',
                                    {'edit': '67890',
                                     'category': '789',
                                     'subcategory-789': '123',
                                     'dname': 'Example 2',
                                     'message': b'testval',
                                     'submitbutton': '1'}),
                          mock.call('lodge_dispatch',
                                    {'edit': '1234567',
                                     'category': '789',
                                     'subcategory-789': '123',
                                     'dname': 'Example 3',
                                     'message': b'10 5 67890',
                                     'submitbutton': '1'})]
        ins.ns_site.execute.assert_has_calls(expected_calls)

        with open('tests/id_store.json') as f:
            assert json.load(f) == {'template_1': 12345, 'template_2': 67890,
                                    'template_3': 1234567}
