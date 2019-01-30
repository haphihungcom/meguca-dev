import os
from unittest import mock

import pytest

from meguca.plugins.src.dispatch_updater import dispatch_updater


class TestTemplateProcessor():
    @pytest.fixture
    def setup_template(self):
        template = '{% for i in j %}{{ i }}{% endfor %}'

        with open('tests/template_file_test.txt', 'w') as template_file:
            template_file.write(template)

        yield 0

        os.remove('tests/template_file_test.txt')

    def test_process_template(self, setup_template):
        ins = dispatch_updater.DispatchRenderer('tests', {'j': [1, 2, 3]})

        assert ins.render_dispatch('template_file_test.txt') == '123'


class TestDispatchUpdater():
    @pytest.fixture
    def setup_templates(self):
        templates = {'tests/template_1.txt': '{% for i in j %}{{ i }}{% endfor %}',
                     'tests/template_2.txt': '{{ x }}'}

        for template_filename, template_content in templates.items():
            with open(template_filename, 'w') as template_file:
                template_file.write(template_content)

        yield 0

        for template_filename in templates.keys():
            os.remove(template_filename)

    def test_update_dispatch(self):
        ins = dispatch_updater.DispatchUpdater()
        ins.ns_site = mock.Mock(execute=mock.Mock())
        template_info = {'Id': 12345, 'Title': 'Test',
                         'Category': 123, 'Subcategory': 456}

        ins.update_dispatch(template_info, 'abc')

        ins.ns_site.execute.assert_called_with('lodge_dispatch',
                                               {'edit': '12345',
                                                'category': '123',
                                                'subcategory-123': '456',
                                                'dname': 'Test',
                                                'message': 'abc',
                                                'submitbutton': '1'})

    def test_run_multiple_dispatches(self, setup_templates):
        data = {'j': [1, 2, 3], 'x': 1}
        mocked_ns_site = mock.Mock(execute=mock.Mock())
        config = {'General': {'TemplateDirectory': 'tests'},
                  'Dispatches': {'template_1.txt': {'Id': 12345, 'Title': 'Example 1',
                                                'Category': 123, 'Subcategory': 456},
                                 'template_2.txt': {'Id': 67890, 'Title': 'Example 2',
                                                'Category': 789, 'Subcategory': 123}}}
        ins = dispatch_updater.DispatchUpdater()
        ins.plg_config = config

        ins.run(data=data, ns_site=mocked_ns_site)

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
                                     'message': '1',
                                     'submitbutton': '1'})]
        mocked_ns_site.execute.assert_has_calls(expected_calls)




