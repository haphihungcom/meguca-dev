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


class TestGenList():
    def test_no_tag(self):
        assert filters.gen_list(['1', '2', '3'], tag=None) == '1, 2, 3'

    def test_with_tag_no_param(self):
        assert filters.gen_list(['1', '2', '3'], tag='a') == '[a]1[/a], [a]2[/a], [a]3[/a]'

    def test_with_tag_and_param(self):
        assert filters.gen_list(['1', '2', '3'], tag='a', tag_modifier='1') == '[a=1]1[/a], [a=1]2[/a], [a=1]3[/a]'
