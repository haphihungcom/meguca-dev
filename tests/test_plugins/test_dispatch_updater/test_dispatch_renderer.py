import os
import shutil
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

    def test_get_custom_vars(self):
        ins = dispatch_renderer.CustomVars('')
        ins._custom_vars = {'foo': {'bar': 'john'}}

        assert ins.custom_vars == {'foo': {'bar': 'john'}}


class TestBBCodeParser():
    @pytest.fixture(scope='class')
    def setup_formatters(self):
        simple_bb_formatters = {'tag1': {'template': '[tagr1]%(value)s[/tagr1]'},
                                'tag2': {'template': '[tagr2]%(value)s[/tagr2]'}}

        with open('simple_bb.toml', 'w') as f:
            toml.dump(simple_bb_formatters, f)

        yield 0

        os.remove('simple_bb.toml')

    def test_load_formatters(self, setup_formatters):
        ins = dispatch_renderer.BBParser('simple_bb.toml', 'tests/resources/bb_formatters.py',
                                         '', '')

        assert ins.parser.format('[dar][tag1]test[/tag1][/dar]') == '[abc][tagr1]test[/tagr1][/abc]'

    def test_load_formatters_without_simple_formatter_file(self, setup_formatters):
        ins = dispatch_renderer.BBParser('', 'tests/resources/bb_formatters.py', '', '')

        assert ins.parser.format('[dar]test[/dar]') == '[abc]test[/abc]'

    def test_load_formatters_without_formatter_file(self, setup_formatters):
        ins = dispatch_renderer.BBParser('simple_bb.toml', '', '', '')

        assert ins.parser.format('[tag1]test[/tag1]') == '[tagr1]test[/tagr1]'

    def test_format_with_simple_formatters(self, setup_formatters):
        ins = dispatch_renderer.BBParser('simple_bb.toml', 'tests/resources/bb_formatters.py',
                                         '', '')

        assert ins.format('[tag1]abc[/tag1]') == '[tagr1]abc[/tagr1]'

    def test_format_with_no_custom_vars_and_config(self, setup_formatters):
        ins = dispatch_renderer.BBParser('simple_bb.toml', 'tests/resources/bb_formatters.py',
                                         '', '')

        assert ins.format('[dar]test[/dar]') == '[abc]test[/abc]'

    def test_format_with_custom_vars_and_config(self, setup_formatters):
        ins = dispatch_renderer.BBParser('simple_bb.toml', 'tests/resources/bb_formatters.py',
                                         custom_vars={'key1': 'val1'},
                                         config={'conf1': 'val1'})

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

    def test_render_dispatch(self, setup_template):
        data = {'j': [1, 2, 3]}
        config = {'conf1': 'val1'}
        ins = dispatch_renderer.Renderer('tests', 'tests/resources/filters.py',
                                         'tests/simple_bb_formatters.toml',
                                         'tests/resources/bb_formatters.py',
                                         'tests/custom_vars.toml', config)
        ins.update_data(data)

        result = ('[a]1and1[/a][a]2and1[/a][a]3and1[/a]'
                  '[vnm=test1][efg=val1][xyz=val1]marry[/xyz][/efg][/vnm]')
        assert ins.render_dispatch('template.txt') == result

