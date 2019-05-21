import os
import shutil
from unittest import mock

import pytest
import toml

from meguca.plugins.src.dispatch_updater import dispatch_renderer
from meguca.plugins.src.dispatch_updater import exceptions


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

        with pytest.raises(exceptions.BBParserError):
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

        with pytest.raises(exceptions.BBParserError):
            ins = dispatch_renderer.BBParser(config, '', '')

    @pytest.fixture
    def setup_func_file(self):
        with open('func.py', 'w') as f:
            f.write('')

        yield

        os.remove('func.py')

    def test_load_formatter_with_empty_func_file(self):
        config = {'simple_formatters': {},
                  'formatters': {'test': {'func_name': 'abc',
                                          'func_path': 'func.py',
                                          'render_embedded': True,
                                          'newline_closes': False,
                                          'same_tag_closes': False,
                                          'standalone': False,
                                          'strip': False,
                                          'swallow_trailing_newline': False}}}

        with pytest.raises(exceptions.BBParserError):
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
    @pytest.fixture
    def setup_template(self):
        template = '{% for i in j %}{{ i|filter1(2) }} {{ i|filter2(3) }} {% endfor %}'
        with open('tests/template.txt', 'w') as f:
            f.write(template)

        yield 0

        os.remove('tests/template.txt')

    def test_load_filters(self):
        ins = dispatch_renderer.TemplateRenderer('tests', 'tests/resources/filters.py')

        assert ins.env.filters['filter1']

    def test_load_filters_with_no_filters(self):
        ins = dispatch_renderer.TemplateRenderer('tests', '')
        assert 'filter1' not in ins.env.filters

    def test_render_with_filters(self, setup_template):
        ins = dispatch_renderer.TemplateRenderer('tests', 'tests/resources/filters.py')

        assert ins.render('template.txt',
                          context={'j': [1, 2]}) == '1 2 1and3 2 2 2and3 '

class TestDispatchRenderer():
    @pytest.fixture
    def setup_template(self):
        template = ('{% for i in j %}[test]{{ i|filter2(1) }}[/test]{% endfor %}'
                    '[moo=test1][foo][bar]{{ john.dave }}[/bar][/foo][/moo]')
        custom_vars = {'john': {'dave': 'marry'}, 'key1': 'val1'}
        simple_bb_formatters = {'test': {'template': '[a]%(value)s[/a]'}}

        with open('tests/template.txt', 'w') as f:
            f.write(template)

        toml.dump(custom_vars, open('tests/custom_vars.toml', 'w'))
        toml.dump(simple_bb_formatters, open('tests/simple_bb_formatters.toml', 'w'))

        yield 0

        os.remove('tests/template.txt')
        os.remove('tests/custom_vars.toml')
        os.remove('tests/simple_bb_formatters.toml')

    def test_render(self, setup_template):
        data = {'j': [1, 2, 3]}
        config = {'conf1': 'val1'}
        ins = dispatch_renderer.Renderer('tests', 'tests/resources/filters.py',
                                         'tests/simple_bb_formatters.toml',
                                         'tests/resources/bb_formatters.py',
                                         'tests/custom_vars.toml', config)
        ins.update_data(data)

        result = ('[a]1and1[/a][a]2and1[/a][a]3and1[/a]'
                  '[vnm=test1][efg=val1][xyz=val1]marry[/xyz][/efg][/vnm]')
        assert ins.render('template.txt') == result

