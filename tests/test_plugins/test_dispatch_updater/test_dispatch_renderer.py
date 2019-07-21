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


class TestBBCodeParser():
    def test_load_formatters(self):
        ins = dispatch_renderer.BBParser(toml.load('tests/resources/bb_formatters.toml'),
                                         '', '')

        assert ins.parser.format('[dar][tag1]test[/tag1][/dar]') == '[abc][tagr1]test[/tagr1][/abc]'

    def test_load_formatters_with_non_existent_func_file(self):
        config = {'simple_formatters': {},
                  'formatters': {'test': {'func_name': 'abc',
                                          'func_path': 'foobar.py',
                                          'render_embedded': True,
                                          'newline_closes': False,
                                          'same_tag_closes': False,
                                          'standalone': False,
                                          'strip': False,
                                          'swallow_trailing_newline': False}}}

        with pytest.raises(FileNotFoundError):
            ins = dispatch_renderer.BBParser(config, '', '')

    def test_load_formatter_with_non_existent_func(self):
        config = {'simple_formatters': {},
                  'formatters': {'test': {'func_name': 'abc',
                                          'func_path': 'tests/resources/bb_formatters.py',
                                          'render_embedded': True,
                                          'newline_closes': False,
                                          'same_tag_closes': False,
                                          'standalone': False,
                                          'strip': False,
                                          'swallow_trailing_newline': False}}}

        with pytest.raises(NameError):
            ins = dispatch_renderer.BBParser(config, '', '')

    def test_format_with_simple_formatters(self):
        ins = dispatch_renderer.BBParser(toml.load('tests/resources/bb_formatters.toml'),
                                         '', '')

        assert ins.format('[tag1]abc[/tag1]') == '[tagr1]abc[/tagr1]'

    def test_format_with_no_custom_vars_and_config(self):
        ins = dispatch_renderer.BBParser(toml.load('tests/resources/bb_formatters.toml'),
                                         '', '')
        assert ins.format('[dar]test[/dar]') == '[abc]test[/abc]'

    def test_format_with_custom_vars_and_config(self):
        ins = dispatch_renderer.BBParser(toml.load('tests/resources/bb_formatters.toml'),
                                         custom_vars={'key1': 'val1'},
                                         ext_config={'conf1': 'val1'})

        assert ins.format('[foo][bar]test[/bar][/foo]') == '[efg=val1][xyz=val1]test[/xyz][/efg]'


class TestTemplateRenderer():
    def test_load_filters(self):
        ins = dispatch_renderer.TemplateRenderer('tests', 'tests/resources/filters.py', '')

        assert ins.env.filters['filter1']

    def test_load_filters_with_no_filters(self):
        ins = dispatch_renderer.TemplateRenderer('tests', '', '')
        assert 'filter1' not in ins.env.filters

    @pytest.mark.usefixtures('mock_templates')
    def test_validate_templates_no_error(self, mock_templates, caplog):
        caplog.set_level(logging.ERROR)

        mock_templates({'tests/template_1.txt': '{{ a }}',
                        'tests/template_2.txt': '{{ b }}'})
        ins = dispatch_renderer.TemplateRenderer('tests', '', 'txt')

        ins.validate_templates()

        for record in caplog.records:
            assert record.levelname != 'ERROR'

    @pytest.mark.usefixtures('mock_templates')
    def test_validate_templates_with_syntax_error(self, mock_templates, caplog):
        """Validate templates with syntax errors. Should log error.
        """

        caplog.set_level(logging.ERROR)

        mock_templates({'tests/template_1.txt': '{{ a }',
                        'tests/template_2.txt': '{{ b }'})
        ins = dispatch_renderer.TemplateRenderer('tests', '', 'txt')

        ins.validate_templates()

        for record in caplog.records:
            assert record.levelname == 'ERROR'

    @pytest.mark.usefixtures('mock_templates')
    def test_render_with_filters(self, mock_templates):
        mock_templates({'tests/template.txt': '{% for i in j %}{{ i|filter1(2) }} {{ i|filter2(3) }} {% endfor %}'})
        ins = dispatch_renderer.TemplateRenderer('tests', 'tests/resources/filters.py', 'txt')

        assert ins.render('template',
                          context={'j': [1, 2]}) == '1 2 1and3 2 2 2and3 '


class TestDispatchRenderer():
    @pytest.mark.usefixtures('mock_templates', 'toml_files')
    @pytest.fixture
    def setup_template(self, mock_templates, toml_files):
        mock_templates({'tests/template.txt': ('{% for i in j %}[tag1]{{ i|filter2(1) }}[/tag1]{% endfor %}'
                                               '[dar]{{ john.dave }}{{ current_dispatch }}[/dar]')})

        toml_files({'tests/custom_vars.toml': {'john': {'dave': 'marry'},
                                               'key1': 'val1'}})

        yield

    def test_init_with_non_existent_bb_config_file(self):
        with pytest.raises(FileNotFoundError):
            ins = dispatch_renderer.Renderer('tests', 'tests/resources/filters.py', '',
                                             'tests/custom_vars.toml', 'txt', {})

    def test_render(self, setup_template):
        data = {'j': [1, 2, 3]}
        config = {'conf1': 'val1'}
        ins = dispatch_renderer.Renderer('tests', 'tests/resources/filters.py',
                                         'tests/resources/bb_formatters.toml',
                                         'tests/custom_vars.toml', 'txt', config)
        ins.update_data(data)

        expected = ('[tagr1]1and1[/tagr1][tagr1]2and1[/tagr1][tagr1]3and1[/tagr1]'
                    '[abc]marrytemplate[/abc]')
        assert ins.render('template') == expected

