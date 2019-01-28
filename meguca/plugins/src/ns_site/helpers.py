from html import parser


class LocalIdParser(parser.HTMLParser):
    """Extract localid from HTML."""

    local_id = None

    def handle_starttag(self, tag, attrs):
        if tag == 'input' and ('name', 'localid') in attrs:
            self.local_id = dict(attrs)['value']

    def get_id(self):
        return self.local_id


class ErrorParser(parser.HTMLParser):
    """Extract error text from HTML."""

    error = None
    is_error = False

    def handle_starttag(self, tag, attrs):
        if tag == 'p' and ('class', 'error') in attrs:
            self.is_error = True

    def handle_data(self, data):
        if self.is_error:
            self.error = data
            self.is_error = False

    def get_error(self):
        return self.error
