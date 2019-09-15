import os

import pytest
import toml

from meguca.dispatch_templates.bbcode import complex_formatters


STD_URL = '[url=https://www.nationstates.net/page=dispatch/id={}][color=#ff9900]{}[/color][/url]'


class TestURL():
    @pytest.fixture(scope='class')
    def context(self):
        yield {'dispatch_info': {'abc': {'id': 1234}},
               'urls': {'efg': 'https://www.wikipedia.org'}}

    def test_url_with_full_url(self, context):
        ins = complex_formatters.Url()

        r = ins.format('url', 'foo', options={'url': 'https://www.google.com'},
                       parent=None, context=context)

        assert r == '[url=https://www.google.com][color=#ff9900]foo[/color][/url]'

    def test_url_with_special_url(self, context):
        ins = complex_formatters.Url()

        r = ins.format('url', 'foo', options={'url': 'efg'},
                       parent=None, context=context)

        assert r == '[url=https://www.wikipedia.org][color=#ff9900]foo[/color][/url]'

    def test_url_with_special_dispatch_url(self, context):
        ins = complex_formatters.Url()

        r = ins.format('url', 'foo', options={'url': 'abc'},
                       parent=None, context=context)

        assert r == STD_URL.format('1234', 'foo')

    def test_url_with_non_existent_special_url(self, context):
        ins = complex_formatters.Url()

        r = ins.format('url', 'foo', options={'url': 'bar'},
                       parent=None, context=context)

        assert r == '[url=bar][color=#ff9900]foo[/color][/url]'

    def test_url_with_special_dispatch_url_contains_anchor(self, context):
        ins = complex_formatters.Url()

        r = ins.format('url', 'foo', options={'url': 'abc#cool'},
                       parent=None, context=context)

        assert r == STD_URL.format('1234#cool', 'foo')


class TestRef():
    def test_ref_with_list_element(self):
        ins = complex_formatters.Ref()

        r = ins.format('ref', '[*]foo[*]bar', options={},
                       parent=None, context=None)

        assert r == ('[font=Avenir, Segoe UI, sans-serif][size=120][color=#019aed][b]Reference: [/b]'
                     '[/color][/size][/font][list][*]foo[*]bar[/list]')

    def test_ref_without_list_element(self):
        ins = complex_formatters.Ref()

        r = ins.format('ref', 'foo', options={},
                       parent=None, context=None)

        assert r == ('[font=Avenir, Segoe UI, sans-serif][size=120][color=#019aed][b]Reference: [/b]'
                     '[/color]foo[/size][/font]')


class TestLaw():
    @pytest.fixture(scope='class')
    def setup(self):
        config = {'laws': {'law_1': {'alt_names': ['Saw 1', 'Daw 1']},
                           'law_2': {},
                           'law_3': {'alt_names': ['Paw 3']}}}
        with open('test.toml', 'w') as f:
            toml.dump(config, f)

        context = {'dispatch_info': {'law_1': {'id': 1234},
                                     'law_2': {'id': 5678},
                                     'law_3': {'id': 9012}}}
        ins = complex_formatters.Law
        ins.config = {'laws_config_path': 'test.toml',
                      'citation_pattern': ('(Section ((?P<sec>\d+), ))?(((\d+), )+)'
                                           '?(Article (?P<art>\w+) of )?(?P<law>.+)'),
                      'article_format': 'a{}',
                      'section_format': '_s{}'}
        ins = complex_formatters.Law()

        yield ins, context

        os.remove('test.toml')

    def test_law_with_only_law_name(self, setup):
        ins, context = setup

        r = ins.format('law', 'The Law 1', options={},
                       parent=None, context=context)

        assert r == STD_URL.format('1234', 'The Law 1')

    def test_law_with_alt_law_name(self, setup):
        ins, context = setup

        r = ins.format('law', 'the Daw 1', options={},
                       parent=None, context=context)

        assert r == STD_URL.format('1234', 'the Daw 1')

    def test_law_with_only_article_and_law_name(self, setup):
        ins, context = setup

        r = ins.format('law', 'Article 5 of the Law 2',
                       options={}, parent=None, context=context)

        assert r == STD_URL.format('5678#a5', 'Article 5 of the Law 2')

    def test_law_with_section_roman_article_law_name(self, setup):
        ins, context = setup

        r = ins.format('law', 'Section 7, Article V of the Law 3',
                       options={}, parent=None, context=context)

        assert r == STD_URL.format('9012#aV_s7', 'Section 7, Article V of the Law 3')

    def test_law_with_many_sections_one_article_law_name(self, setup):
        ins, context = setup

        r = ins.format('law', 'Section 5, 6, Article 5 of the Law 1',
                       options={}, parent=None, context=context)

        assert r == STD_URL.format('1234#a5_s5', 'Section 5, 6, Article 5 of the Law 1')

    def test_law_not_found(self, setup):
        ins, context = setup

        r = ins.format('law', 'Law 6', options={},
                       parent=None, context=context)

        assert r == '[url=][color=#ff9900]Law 6[/color][/url]'