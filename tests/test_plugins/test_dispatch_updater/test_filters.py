import jinja2

from meguca.plugins.src.dispatch_updater import filters


class TestNation():
    def test_default(self):
        assert filters.nation('test') == '[nation]test[/nation]'

    def test_with_modifier(self):
        assert filters.nation('test', 'noflag') == '[nation=noflag]test[/nation]'


class TestRegion():
    def test_default(self):
        assert filters.region('test') == '[region]test[/region]'
