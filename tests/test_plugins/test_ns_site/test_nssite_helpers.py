from meguca.plugins.src.ns_site import helpers


class TestParsers():
    def test_parse_localid_from_html_contains_localid_attr_in_input_tag(self):
        html = '<input type="hidden" name="localid" value="123456">'
        parser = helpers.LocalIdParser()
        parser.feed(html)

        assert parser.get_id() == '123456'

    def test_parse_error_from_html_contains_error_in_p_tag_class_error(self):
        html = '<p class="error">Error</p>'
        parser = helpers.ErrorParser()
        parser.feed(html)

        assert parser.get_error() == 'Error'
