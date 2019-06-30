import pytest

from meguca.dispatch_templates.bbcode import formatters


class TestURL():
    @pytest.fixture(scope='class')
    def context(self):
        yield {'config': {'dispatches': {'abc': {'id': 1234}}},
               'custom_vars': {'urls': {'efg': 'https://www.wikipedia.org'}}}

    def test_url_with_full_url(self, context):
        r = formatters.url('url', 'foo', options={'url': 'https://www.google.com'},
                           parent=None, context=context)

        assert r == '[url=https://www.google.com][color=#ff9900]foo[/color][/url]'

    def test_url_with_special_url(self, context):
        r = formatters.url('url', 'foo', options={'url': 'efg'},
                           parent=None, context=context)

        assert r == '[url=https://www.wikipedia.org][color=#ff9900]foo[/color][/url]'

    def test_url_with_special_dispatch_url(self, context):
        r = formatters.url('url', 'foo', options={'url': 'abc'},
                           parent=None, context=context)

        assert r == '[url=https://www.nationstates.net/page=dispatch/id=1234][color=#ff9900]foo[/color][/url]'

    def test_url_with_non_existent_special_url(self, context):
        r = formatters.url('url', 'foo', options={'url': 'bar'},
                           parent=None, context=context)

        assert r == '[url=bar][color=#ff9900]foo[/color][/url]'

    def test_url_with_special_dispatch_url_contains_anchor(self, context):
        r = formatters.url('url', 'foo', options={'url': 'abc#cool'},
                           parent=None, context=context)

        assert r == '[url=https://www.nationstates.net/page=dispatch/id=1234#cool][color=#ff9900]foo[/color][/url]'


class TestRef():
    def test_ref_with_list_element(self):
        r = formatters.ref('ref', '[*]foo[*]bar', options={},
                           parent=None, context=None)

        assert r == ('[font=Avenir, Segoe UI, sans-serif][size=120][color=#019aed][b]Reference: [/b]'
                     '[/color][/size][/font][list][*]foo[*]bar[/list]')

    def test_ref_without_list_element(self):
        r = formatters.ref('ref', 'foo', options={},
                           parent=None, context=None)

        assert r == ('[font=Avenir, Segoe UI, sans-serif][size=120][color=#019aed][b]Reference: [/b]'
                     '[/color]foo[/size][/font]')
