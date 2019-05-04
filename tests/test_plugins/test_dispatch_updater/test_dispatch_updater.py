import os
import shutil
from unittest import mock

import pytest
import toml

from meguca.plugins.src.dispatch_updater import dispatch_renderer
from meguca.plugins.src.dispatch_updater import dispatch_updater


class TestDispatchUpdater():
    @pytest.fixture
    def setup_templates(self):
        templates = {'tests/template_1.txt': '{% for i in j %}{{ i }}{% endfor %}',
                     'tests/template_2.txt': 'bar'}

        for template_filename, template_content in templates.items():
            with open(template_filename, 'w') as template_file:
                template_file.write(template_content)

        yield 0

        for template_filename in templates.keys():
            os.remove(template_filename)

    def test_update_dispatch(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.ns_site = mock.Mock(execute=mock.Mock())
        template_info = {'id': 12345, 'title': 'Test',
                         'category': 123, 'sub_category': 456}

        ins.update_dispatch(template_info, 'abc')

        ins.ns_site.execute.assert_called_with('lodge_dispatch',
                                               {'edit': '12345',
                                                'category': '123',
                                                'subcategory-123': '456',
                                                'dname': 'Test',
                                                'message': 'abc',
                                                'submitbutton': '1'})

    def test_run_multiple_dispatches(self, setup_templates):
        data = mock.Mock(get_bare_obj=mock.Mock(return_value={'j': [1, 2, 3]}))
        mocked_ns_site = mock.Mock(execute=mock.Mock())
        config = {'general': {'template_dir_path': 'tests', 'filters_path': '',
                              'custom_vars_path': '', 'simple_bb_path': '',
                              'bb_path': '', 'template_file_ext': 'txt'},
                  'dispatches': {'template_1': {'id': 12345, 'title': 'Example 1',
                                                 'category': 123, 'sub_category': 456},
                                 'template_2': {'id': 67890, 'title': 'Example 2',
                                                'category': 789, 'sub_category': 123}}}
        ins = dispatch_updater.DispatchUpdater()
        ins.plg_config = config
        ins.prepare(mocked_ns_site)

        ins.run(data=data)

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
                                     'message': 'bar',
                                     'submitbutton': '1'})]
        mocked_ns_site.execute.assert_has_calls(expected_calls)
