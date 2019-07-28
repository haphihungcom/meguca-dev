import os
from unittest import mock

import pytest
import toml

from meguca.plugins.src.dispatch_updater import BBCode
from meguca.plugins.src.dispatch_updater import bb_parser


class TestBBParserCore():
    def test_add_simple_formatter(self):
        ins = bb_parser.BBParserCore()
        add_simple_formatter = mock.Mock()
        ins.parser.add_simple_formatter = add_simple_formatter

        ins.add_simple_formatter('test', 'test', escape_html=True)

        add_simple_formatter.assert_called_with(tag_name='test', format_string='test',
                                                escape_html=True)

    def test_add_complex_formatter(self):
        ins = bb_parser.BBParserCore()
        mock_func = mock.Mock()
        add_formatter = mock.Mock()
        ins.parser.add_formatter = add_formatter

        ins.add_complex_formatter('test', mock_func, escape_html=True)

        add_formatter.assert_called_with(tag_name='test', render_func=mock_func,
                                         escape_html=True)

    def test_format(self):
        ins = bb_parser.BBParserCore()
        mock_format = mock.Mock(return_value='Test')
        ins.parser = mock.Mock(format=mock_format)

        assert ins.format(text='abc', example='123') == 'Test'
        mock_format.assert_called_with('abc', example='123')


class TestBBRegistry():
    def test_register_formatter_class(self):
        @BBCode.register('test', john=True)
        class Test():
            a = 1

        r = bb_parser.BBRegistry().complex_formatters[0]

        assert r['tag_name'] == 'test' and r['john'] == True
        assert r['obj'].a == 1

    @mock.patch('meguca.plugins.src.dispatch_updater.utils.load_classes')
    def test_init_complex_formatters(self, mock):
        ins = bb_parser.BBRegistry

        class Formatter1():
            pass

        class Formatter2():
            pass

        ins.complex_formatters = [{'tag_name': 'test1', 'obj': Formatter1(), 'john': True},
                                  {'tag_name': 'test2', 'obj': Formatter2(), 'john': False}]
        config = {'test1': {'foo': 'bar', 'loo': 'var'},
                  'test2': {'foo2': 'bar2', 'loo2': 'var2'}}

        ins.init_complex_formatters('test.py', config)

        r = ins.complex_formatters
        assert ins.complex_formatters[0]['obj'].config == {'foo': 'bar', 'loo': 'var'}
        assert ins.complex_formatters[1]['obj'].config == {'foo2': 'bar2', 'loo2': 'var2'}

    @mock.patch('meguca.plugins.src.dispatch_updater.utils.load_classes')
    def test_init_complex_formatters_with_non_existent_config(self, mock):
        ins = bb_parser.BBRegistry

        class Formatter1():
            pass

        class Formatter2():
            pass

        ins.complex_formatters = [{'tag_name': 'test1', 'obj': Formatter1(), 'john': True},
                                  {'tag_name': 'test2', 'obj': Formatter2(), 'john': False}]

        ins.init_complex_formatters('test.py', {})

        r = ins.complex_formatters
        assert not hasattr(ins.complex_formatters[0]['obj'], 'config')
        assert not hasattr(ins.complex_formatters[1]['obj'], 'config')

    @mock.patch('meguca.plugins.src.dispatch_updater.utils.load_classes',
                side_effect=FileNotFoundError)
    def test_init_complex_formatters_with_non_existent_file(self, mock):
        ins = bb_parser.BBRegistry()

        with pytest.raises(FileNotFoundError):
            ins.init_complex_formatters('test.py', {})



class TestBBParserLoader():
    @pytest.mark.usefixtures('toml_files')
    def test_load_simple_formatters_with_simple_formatter_file_exists(self, toml_files):
        formatter_config = {'tag1': {'template': 'test1',
                                     'render_embedded': True,
                                     'newline_closes': False},
                            'tag2': {'template': 'test2',
                                     'render_embedded': True,
                                     'newline_closes': False,
                                     'same_tag_closes': True}}
        toml_files({'tests/test.toml': formatter_config})
        config = {'simple_formatter_path': 'tests/test.toml'}
        mock_parser = mock.Mock(add_simple_formatter=mock.Mock())
        ins = bb_parser.BBParserLoader(mock_parser, mock.Mock(), config)

        ins.load_simple_formatters()

        mock_parser.add_simple_formatter.assert_called_with(tag_name='tag2',
                                                            template='test2',
                                                            escape_html=False,
                                                            replace_links=False,
                                                            replace_cosmetic=False,
                                                            render_embedded=True,
                                                            newline_closes=False,
                                                            same_tag_closes=True,
                                                            standalone=False,
                                                            strip=False,
                                                            swallow_trailing_newline=False)

    def test_load_simple_formatters_with_non_configured_simple_formatter_file(self):
        """Nothing should happen.
        """

        mock_parser = mock.Mock(add_simple_formatter=mock.Mock())
        ins = bb_parser.BBParserLoader(mock.Mock(), mock.Mock(), {})

        ins.load_simple_formatters()

        mock_parser.add_simple_formatter.assert_not_called()

    def test_load_simple_formatters_with_non_existent_simple_formatter_file(self):
        """Nothing should happen.
        """

        mock_parser = mock.Mock(add_simple_formatter=mock.Mock())
        ins = bb_parser.BBParserLoader(mock_parser, mock.Mock(),
                                       {'simple_formatter_path': 'ghhj'})

        ins.load_simple_formatters()

        mock_parser.add_simple_formatter.assert_not_called()

    @pytest.mark.usefixtures('toml_files')
    def test_load_simple_formatters_with_no_template_simple_formatter_file(self, toml_files):
        """Nothing should happen.
        """

        formatter_config = {'tag1': {'render_embedded': True,
                                     'newline_closes': False},
                            'tag2': {'render_embedded': True,
                                     'newline_closes': False,
                                     'same_tag_closes': True}}
        toml_files({'tests/test.toml': formatter_config})
        config = {'simple_formatter_path': 'tests/test.toml'}
        mock_parser = mock.Mock(add_simple_formatter=mock.Mock())
        ins = bb_parser.BBParserLoader(mock_parser, mock.Mock(), config)

        ins.load_simple_formatters()

        mock_parser.add_simple_formatter.assert_not_called()

    @pytest.fixture
    def mock_bb_registry(self):
        class Test1():
            def format(self):
                pass

        class Test2():
            def format(self):
                pass

        f = [{'tag_name': 'test1', 'obj': Test1(), 'newline_closes': True},
             {'tag_name': 'test2', 'obj': Test2(), 'same_tag_closes': True}]

        ins = mock.Mock(init_complex_formatters=mock.Mock())
        type(ins).complex_formatters = f

        return ins

    def test_load_complex_formatters_with_not_configured_config(self, mock_bb_registry):
        config = {'complex_formatter_path': 'test.py'}
        mock_parser_core = mock.Mock(add_complex_formatter=mock.Mock())
        ins = bb_parser.BBParserLoader(mock_parser_core, mock_bb_registry, config)

        ins.load_complex_formatters()

        mock_bb_registry.init_complex_formatters.assert_called_with('test.py', {})

        f = mock_bb_registry.complex_formatters
        r = mock_parser_core.add_complex_formatter
        r.assert_called_with(tag_name='test2',
                             render_func=f[1]['obj'].format,
                             escape_html=False,
                             replace_links=False,
                             replace_cosmetic=False,
                             render_embedded=True,
                             newline_closes=False,
                             same_tag_closes=True,
                             standalone=False,
                             strip=False,
                             swallow_trailing_newline=False)

    def test_load_complex_formatters_with_non_existent_config(self, mock_bb_registry):
        config = {'complex_formatter_path': 'test.py',
                  'complex_formatter_config_path': 'ghghgh'}
        mock_parser_core = mock.Mock(add_complex_formatter=mock.Mock())
        ins = bb_parser.BBParserLoader(mock_parser_core, mock_bb_registry, config)

        ins.load_complex_formatters()

        mock_bb_registry.init_complex_formatters.assert_called_with('test.py', {})

        f = mock_bb_registry.complex_formatters
        r = mock_parser_core.add_complex_formatter
        r.assert_called_with(tag_name='test2',
                             render_func=f[1]['obj'].format,
                             escape_html=False,
                             replace_links=False,
                             replace_cosmetic=False,
                             render_embedded=True,
                             newline_closes=False,
                             same_tag_closes=True,
                             standalone=False,
                             strip=False,
                             swallow_trailing_newline=False)

    @pytest.mark.usefixtures('toml_files')
    def test_load_complex_formatters_with_config(self, mock_bb_registry, toml_files):
        formatter_config = {'test1': {'key1': 'val1'}}
        toml_files({'tests/test.toml': formatter_config})
        config = {'complex_formatter_path': 'test.py',
                  'complex_formatter_config_path': 'tests/test.toml'}
        mock_parser_core = mock.Mock(add_complex_formatter=mock.Mock())
        ins = bb_parser.BBParserLoader(mock_parser_core, mock_bb_registry, config)

        ins.load_complex_formatters()

        mock_bb_registry.init_complex_formatters.assert_called_with('test.py', formatter_config)

        f = mock_bb_registry.complex_formatters
        r = mock_parser_core.add_complex_formatter
        r.assert_called_with(tag_name='test2',
                             render_func=f[1]['obj'].format,
                             escape_html=False,
                             replace_links=False,
                             replace_cosmetic=False,
                             render_embedded=True,
                             newline_closes=False,
                             same_tag_closes=True,
                             standalone=False,
                             strip=False,
                             swallow_trailing_newline=False)

    def test_load_complex_formatters_with_non_configured_complex_formatter_path(self):
        mock_parser_core = mock.Mock(add_complex_formatter=mock.Mock())
        ins = bb_parser.BBParserLoader(mock_parser_core, mock.Mock(), {})

        ins.load_complex_formatters()

        mock_parser_core.add_complex_formatter.assert_not_called()


class TestBBParserIntegration():
    def test_integration(self):
        config = {'simple_formatter_path': 'tests/resources/bb_simple_formatters.toml',
                  'complex_formatter_path': 'tests/resources/bb_complex_formatters.py',
                  'complex_formatter_config_path': 'tests/resources/bb_complex_formatter_config.toml'}
        ins = bb_parser.BBParser(config)
        text = ('[dar]john[bar]doe[/bar][/dar][foo]marry[tag1]curie[/tag1][/foo]'
                '[moo=123][tag2]mirai[/tag2][/moo]')

        r = ins.format(text, example={'hoo': 'cool'})

        assert r == ('[abc]john[xyz=testval]doe[/xyz][/abc][efg=cool]marry[tag1]curie[/tag1][/efg]'
                     '[vnm=123][tagr2]mirai[/tagr2][/vnm]')