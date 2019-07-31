import os
import shutil
import logging
from unittest import mock

import pytest
import toml

from meguca.plugins.src.dispatch_updater import dispatch_renderer


class TestCustomVars():
    @pytest.fixture(scope='class')
    def setup_custom_vars_files(self):
        custom_vars_1 = {'foo1': {'bar1': 'john1'}}
        with open('test1.toml', 'w') as f:
            toml.dump(custom_vars_1, f)

        custom_vars_2 = {'foo2': {'bar2': 'john2'}}
        with open('test2.toml', 'w') as f:
            toml.dump(custom_vars_2, f)

        yield 0

        os.remove('test1.toml')
        os.remove('test2.toml')

    def test_load_custom_vars_with_one_file(self, setup_custom_vars_files):
        ins = dispatch_renderer.CustomVars('test1.toml')

        assert ins._custom_vars == {'foo1': {'bar1': 'john1'}}

    def test_load_custom_vars_with_many_files(self, setup_custom_vars_files):
        ins = dispatch_renderer.CustomVars(['test1.toml', 'test2.toml'])

        assert ins._custom_vars == {'foo1': {'bar1': 'john1'},
                                    'foo2': {'bar2': 'john2'}}

    def test_load_custom_vars_with_non_existent_file(self):
        with pytest.raises(FileNotFoundError):
            dispatch_renderer.CustomVars(['asas.toml', 'asss.toml'])

    def test_load_custom_vars_with_no_file(self):
        """Load custom vars if no file is provided.
        Nothing should happen.
        """

        dispatch_renderer.CustomVars([])

    def test_get_custom_vars(self):
        ins = dispatch_renderer.CustomVars('')
        ins._custom_vars = {'foo': {'bar': 'john'}}

        assert ins.custom_vars == {'foo': {'bar': 'john'}}


class TestTemplateRenderer():
    def test_load_filters(self):
        ins = dispatch_renderer.TemplateRenderer('tests', 'tests/resources/filters.py', '')

        assert ins.env.filters['filter1']

    def test_load_filters_with_no_filters(self):
        ins = dispatch_renderer.TemplateRenderer('tests', '', '')
        assert 'filter1' not in ins.env.filters

    @pytest.mark.usefixtures('text_files')
    def test_validate_templates_no_error(self, text_files, caplog):
        caplog.set_level(logging.ERROR)

        text_files({'tests/template_1.txt': '{{ a }}',
                    'tests/template_2.txt': '{{ b }}'})
        ins = dispatch_renderer.TemplateRenderer('tests', '', 'txt')

        ins.validate_templates()

        for record in caplog.records:
            assert record.levelname != 'ERROR'

    @pytest.mark.usefixtures('text_files')
    def test_validate_templates_with_syntax_error(self, text_files, caplog):
        """Validate templates with syntax errors. Should log error.
        """

        caplog.set_level(logging.ERROR)

        text_files({'tests/template_1.txt': '{{ a }',
                    'tests/template_2.txt': '{{ b }'})
        ins = dispatch_renderer.TemplateRenderer('tests', '', 'txt')

        ins.validate_templates()

        for record in caplog.records:
            assert record.levelname == 'ERROR'

    @pytest.mark.usefixtures('text_files')
    def test_render_with_filters(self, text_files):
        text_files({'tests/template.txt': '{% for i in j %}{{ i|filter1(2) }} {{ i|filter2(3) }} {% endfor %}'})
        ins = dispatch_renderer.TemplateRenderer('tests', 'tests/resources/filters.py', 'txt')

        assert ins.render('template',
                          context={'j': [1, 2]}) == '1 2 1and3 2 2 2and3 '


class TestDispatchRenderer():
    @pytest.mark.usefixtures('text_files', 'toml_files')
    @pytest.fixture
    def setup_template(self, text_files, toml_files):
        text_files({'tests/test1.txt': ('{% for i in data_products.j %}[tag1]{{ i|filter2(1) }}[/tag1]{% endfor %}'
                                       '[dar]{{ john.dave }}{{ current_dispatch.name }}[/dar][bar]'
                                       '{{ ext_config.meguca.key1 }}[/bar]')})

        toml_files({'tests/custom_vars.toml': {'john': {'dave': 'marry'},
                                               'key1': 'val1'}})

    def test_render(self, setup_template):
        data = {'j': [1, 2, 3]}
        dispatch_info = {'test1': {'id': 1234567, 'title': 'ABC'},
                         'test2': {'id': 7890123, 'title': 'DEF'}}
        plg_config = {'conf1': 'val1'}
        config = {'meguca': {'key1': 'val1'}}
        renderer_config = {'template': {'template_dir_path': 'tests',
                                        'filters_path': 'tests/resources/filters.py',
                                        'template_file_ext': 'txt'},
                           'bbcode': {'simple_formatter_path': 'tests/resources/bb_simple_formatters.toml',
                                      'complex_formatter_path': 'tests/resources/bb_complex_formatters.py',
                                      'complex_formatter_config_path': 'tests/resources/bb_complex_formatter_config.toml'},
                           'custom_vars_path': 'tests/custom_vars.toml'}
        ins = dispatch_renderer.Renderer(renderer_config)

        ins.update_ctx(data, plg_config, config, dispatch_info)

        expected = ('[tagr1]1and1[/tagr1][tagr1]2and1[/tagr1][tagr1]3and1[/tagr1]'
                    '[abc]marrytest1[/abc][xyz=testval]val1[/xyz]')
        assert ins.render('test1') == expected

