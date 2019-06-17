from meguca.dispatch_templates.filters import filters


class TestNation():
    def test_default(self):
        assert filters.nation('test') == '[nation]test[/nation]'

    def test_with_modifier(self):
        assert filters.nation('test', 'noflag') == '[nation=noflag]test[/nation]'


class TestRegion():
    def test_default(self):
        assert filters.region('test') == '[region]test[/region]'


class TestGenList():
    def test_with_default_tag(self):
        assert filters.gen_list(['1', '2', '3']) == '[nation]1[/nation], [nation]2[/nation], [nation]3[/nation]'

    def test_with_custom_tag(self):
        assert filters.gen_list(['1', '2', '3'], start_tag='[a]', end_tag='[/a]') == '[a]1[/a], [a]2[/a], [a]3[/a]'


class TestGenTableList():
    def test_with_default_tag_and_column_num(self):
        expected = '[tr][td][nation]1[/nation][/td][td][nation]2[/nation][/td][td][nation]3[/nation][/td][/tr]'
        assert filters.gen_table_tags(['1', '2', '3']) == expected

    def test_with_custom_tag_and_column_num(self):
        expected = '[tr][td][a]1[/a][/td][td][a]2[/a][/td][/tr][tr][td][a]3[/a][/td][/tr]'
        assert filters.gen_table_tags(['1', '2', '3'], column_num=2, start_tag='[a]', end_tag='[/a]') == expected