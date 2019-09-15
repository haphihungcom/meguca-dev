import os
from unittest import mock

import pytest
import toml
import bs4

from meguca.plugins.src import laws_updater


class TestGenAnchor():
    def test_gen_anchor(self):
        lut = {'section': {'match': '\((\d+)\) .+',
                           'anchor_link': 's\g<1>'},
               'article': {'match': '(\w+)\. .+',
                           'anchor_link': 'a\g<1>'},
               'subsection': {'match': '([a-z]+)\. .+',
                              'anchor_link': '\g<1>'}}
        ins = laws_updater.GenAnchor(lut)

        r1 = ins.get_anchor('1. ABCD')
        ins.get_anchor('(1) EFB')
        r2 = ins.get_anchor('(2) GHJ')
        r3 = ins.get_anchor('asasaas')
        ins.get_anchor('2. POL')
        r4 = ins.get_anchor('(1) AKL')
        r5 = ins.get_anchor('a. AKL')

        assert r1 == '[anchor=a1][/anchor]'
        assert r2 == '[anchor=a1_s2][/anchor]'
        assert r3 == None
        assert r4 == '[anchor=a2_s1][/anchor]'
        assert r5 == '[anchor=a2_s1_a][/anchor]'

class TestGetBBTag():
    def test_get_bb_tag_from_html_element(self):
        html = bs4.BeautifulSoup('<span class="xyz">ABC</span>', 'html.parser')
        lut = {'test': {'name': 'span',
                        'attrs': {'class': ['xyz']},
                        'bb_tag': '[test]{text}[/test]'}}

        tag = laws_updater.get_bb_tag(html.contents[0], lut)

        assert tag == '[test]{text}[/test]'

    def test_get_bb_tag_from_html_element_not_on_lut(self):
        html = bs4.BeautifulSoup('<span class="efj">ABC</span>', 'html.parser')
        lut = {'test': {'name': 'span',
                        'attrs': {'class': ['xyz']},
                        'bb_tag': '[test]{text}[/test]'}}

        tag = laws_updater.get_bb_tag(html.contents[0], lut)

        assert tag == '{text}'


class TestGenBBCode():
    def test_get_bbcode_laws(self):
        lut = {'bold': { 'name': 'span',
                         'attrs': {'class': ['bold'],
                                   'style': 'font-weight: bold;'},
                         'bb_tag': '[b]{text}[/b]' },
               'italic': { 'name': 'span',
                           'attrs': {'class': ['italic'],
                                     'style': 'font-style: italic;'},
                           'bb_tag': '[i]{text}[/i]' },
               'align': { 'name': 'div',
                          'attrs': {'class': ['align'],
                                    'style': 'text-align: center;'},
                          'bb_tag': '[align=center]{text}[/align]' }}
        html = ('<div class="align" style="text-align: center;">  \n'
                '<weird><span class="bold" style="font-weight: bold;">Title</span></weird>  <br />'
                '<span class="italic" style="font-style: italic;">Subtitle</span>  <br />'
                '</div>  '
                '<br />ABCDEF  '
                '<span class="bold" style="font-weight: bold;">  Article</span>')
        soup = bs4.BeautifulSoup(html, 'html.parser')

        r = laws_updater.gen_bbcode(soup, lut, mock.Mock(get_anchor=mock.Mock(return_value=None)),
                                    'br', '[p]{text}[/p]')

        assert r == ('[align=center]\n[b][p]Title[/p][/b] \n'
                     '[i][p]Subtitle[/p][/i] \n[/align] '
                     '\n[p]ABCDEF  [/p][b][p]  Article[/p][/b]')


class TestEmbedJinjaTemplate():
    @pytest.mark.usefixtures('text_files')
    def test_embed_jinja_template_with_existent_std_template_file(self, text_files):
        text_files({'tests/std.txt': '{% block body %} [laws] {% endblock %}'})

        r = laws_updater.embed_jinja_template('ABCD', 'tests/std.txt')

        assert r == '{% block body %} ABCD {% endblock %}'

    @pytest.mark.usefixtures('text_files')
    def test_embed_jinja_template_with_non_existent_std_template_file(self, text_files):

        with pytest.raises(FileNotFoundError):
            laws_updater.embed_jinja_template('ABCD', 'tests/std.txt')


class TestLawsUpdater():
    @pytest.fixture
    def setup_laws_updater(self):
        bb_lut = {'bold': {'name': 'span',
                           'attrs': {'class': ['bold'],
                                     'style': 'font-weight: bold;'},
                           'bb_tag': '[b]{text}[/b]' },
                  'italic': {'name': 'span',
                             'attrs': {'class': ['italic'],
                                       'style': 'font-style: italic;'},
                             'bb_tag': '[i]{text}[/i]' },
                  'align': {'name': 'div',
                            'attrs': {'class': ['align'],
                                      'style': 'text-align: center;'},
                            'bb_tag': '[align=center]{text}[/align]' }}
        anchor_lut = {'section': {'match': '\((\d+)\) .+',
                                  'anchor_link': 's\g<1>'},
                      'article': {'match': '(\w+)\. .+',
                                  'anchor_link': 'a\g<1>'},
                      'subsection': {'match': '([a-z]+)\. .+',
                                     'anchor_link': '\g<1>'}}
        config = {'general': {'dispatch_config_path': 'tests/dispatch_config.toml',
                              'category': 8,
                              'sub_category': 835,
                              'template_ext': 'txt',
                              'template_dir_path': 'tests',
                              'std_template_path': 'tests/std_laws_template.txt'},
                  'bb_lookup': {'container': 'div[class="postbody"]',
                                'default_bb_tag': '[p]{text}[/p]',
                                'line_break_html_tag': 'br',
                                'tags': bb_lut},
                  'anchor_lookup': anchor_lut,
                  'laws': {'test1': {'title': 'Test 1', 'url': 'abc'},
                           'test2': {'title': 'Test 2', 'url': 'xyz'}}}

        ins = laws_updater.LawsUpdater()
        ins.plg_config = config

        return ins

    @pytest.fixture
    def clean_dispatch_config(self):
        yield

        os.remove('tests/dispatch_config.toml')

    def test_update_dispatch_config_with_dispatch_config_not_exist(self, setup_laws_updater,
                                                                   clean_dispatch_config):
        ins = setup_laws_updater

        ins.update_dispatch_config()

        r = {'test1': {'title': 'Test 1', 'category': 8, 'sub_category': 835},
             'test2': {'title': 'Test 2', 'category': 8, 'sub_category': 835}}

        assert toml.load('tests/dispatch_config.toml') == r

    @pytest.mark.usefixtures('toml_files')
    def test_update_dispatch_config_with_dispatch_config_exists(self, setup_laws_updater,
                                                                toml_files):
        """Should update dispatch config file.
        """

        config = {'testa': {'title': 'Test A', 'url': 'xyz'},
                  'testb': {'title': 'Test B', 'url': 'abc'}}
        toml_files({'tests/dispatch_config.toml': config})

        ins = setup_laws_updater

        ins.update_dispatch_config()

        r = {'test1': {'title': 'Test 1', 'category': 8, 'sub_category': 835},
             'test2': {'title': 'Test 2', 'category': 8, 'sub_category': 835}}

        assert toml.load('tests/dispatch_config.toml') == r

    @pytest.fixture
    def clean_dispatches(self):
        yield

        os.remove('tests/test1.txt')
        os.remove('tests/test2.txt')

    @mock.patch('requests.Session.get', return_value=mock.Mock(text='Test'))
    def test_update_laws_dispatches_with_non_existent_dispatches(self, mock_requests_get,
                                                                 setup_laws_updater,
                                                                 clean_dispatches):
        """Should create new dispatch files.
        """

        ins = setup_laws_updater
        ins.get_bbcode_laws = mock.Mock(return_value='Test')

        ins.update_laws_dispatches()

        ins.get_bbcode_laws.assert_called_with('Test')

        with open('tests/test1.txt') as f:
            assert f.read() == 'Test'

        with open('tests/test2.txt') as f:
            assert f.read() == 'Test'

    @pytest.mark.usefixtures('text_files')
    @mock.patch('requests.Session.get', return_value=mock.Mock(text='Test'))
    def test_update_laws_dispatches_with_existent_dispatches(self, mock_requests_get,
                                                             setup_laws_updater,
                                                             text_files):
        """Should update dispatch files to new content.
        """

        text_files({'tests/test1.txt': 'dork',
                    'tests/test2.txt': 'dork'})
        ins = setup_laws_updater
        ins.get_bbcode_laws = mock.Mock(return_value='Test')

        ins.update_laws_dispatches()

        ins.get_bbcode_laws.assert_called_with('Test')

        with open('tests/test1.txt') as f:
            assert f.read() == 'Test'

        with open('tests/test2.txt') as f:
            assert f.read() == 'Test'

    @pytest.fixture
    def clean_dispatch_integration(self):
        yield

        os.remove('tests/tsunamy.txt')

    @pytest.mark.usefixtures('text_files')
    def test_run_integration(self, text_files,
                             setup_laws_updater,
                             clean_dispatch_integration,
                             clean_dispatch_config):
        text_files({'tests/lampshade.txt': 'Empty'})
        text_files({'tests/std_laws_template.txt': '{% block body %} [laws] {% endblock %}'})
        ins = setup_laws_updater
        ins.plg_config['laws'] =  {'lampshade': {'title': 'Lampshade Act', 'url': 'https://test1.html'},
                                   'tsunamy': {'title': 'Tsunamy Act', 'url': 'https://test2.html'}}

        def mock_html(url):
            if url == 'https://test1.html':
                html = ('<div>Mirai Kuriyama </div>\n<div class="postbody">'
                        '<div class="align" style="text-align: center;">\n  '
                        '<span class="bold" style="font-weight: bold;">Lampshade Act  </span>\n<br />'
                        '<span class="italic" style="font-style: italic;">An Act for Testing. </span><br />'
                        '</div>'
                        '<br />Preamble<br />'
                        '<span class="bold" style="font-weight: bold;">1. Article</span>\n   '
                        '<br />(1) Racoon shall be the regional animal.\n'
                        '<br />(2) Failure to feed the racoon results in security actions.</div>')

                return mock.Mock(text=html)

            elif url == 'https://test2.html':
                html = ('<div>Kanna Kamui</div>\n<div class="postbody">'
                        '<div class="align" style="text-align: center;">'
                        '<span class="bold" style="font-weight: bold;">Tsunamy Act</span> <br />'
                        '<span class="italic" style="font-style: italic;">An Act about permanent delegacy. \n</span><br />'
                        '</div><br />'
                        '\n<span class="bold" style="font-weight: bold;">\n  V. Article</span>'
                        '<br />(1) Tsunamy shall be our permanent Delegate.'
                        '<br />(2) Failure to endorse Tsunamy results in lampshade confiscation.   </div>')

                return mock.Mock(text=html)

        with mock.patch('requests.Session.get', side_effect=mock_html):
            ins.run()

        r1 = ('{% block body %} [align=center]\n[b][p]Lampshade Act  [/p][/b]\n\n'
              '[i][p]An Act for Testing. [/p][/i]\n[/align]\n'
              '[p]Preamble[/p]\n'
              '[b][anchor=a1][/anchor][p]1. Article[/p][/b]\n'
              '\n[anchor=a1_s1][/anchor][p](1) Racoon shall be the regional animal.[/p]'
              '\n[anchor=a1_s2][/anchor][p](2) Failure to feed the racoon results in security actions.[/p] {% endblock %}')

        r2 = ('{% block body %} [align=center][b][p]Tsunamy Act[/p][/b] \n'
              '[i][p]An Act about permanent delegacy. [/p][/i]\n[/align]\n'
              '\n[b][anchor=aV][/anchor][p]  V. Article[/p][/b]'
              '\n[anchor=aV_s1][/anchor][p](1) Tsunamy shall be our permanent Delegate.[/p]'
              '\n[anchor=aV_s2][/anchor][p](2) Failure to endorse Tsunamy results in lampshade confiscation.   [/p] {% endblock %}')

        with open('tests/lampshade.txt') as f:
            assert f.read() == r1

        with open('tests/tsunamy.txt') as f:
            assert f.read() == r2

        r3 = {'lampshade': {'title': 'Lampshade Act', 'category': 8, 'sub_category': 835},
              'tsunamy': {'title': 'Tsunamy Act', 'category': 8, 'sub_category': 835}}

        assert toml.load('tests/dispatch_config.toml') == r3
