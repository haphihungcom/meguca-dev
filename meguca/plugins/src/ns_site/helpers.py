from html import parser


class LocalIdParser(parser.HTMLParser):
    """Extract localid from HTML."""

    id = None

    def handle_starttag(self, tag, attrs):
        if tag == "input" and attrs[1][1] == "localid":
            self.id = attrs[2][1]

    def get_id(self):
        return self.id


class ErrorParser(parser.HTMLParser):
    """Extract error text from HTML."""

    error = None
    is_error = False

    def handle_starttag(self, tag, attrs):
        if tag == "p" and attrs[0][1] == "error":
            self.is_error = True

    def handle_data(self, data):
        if self.is_error:
            self.error = data

    def get_error(self):
        return self.error
