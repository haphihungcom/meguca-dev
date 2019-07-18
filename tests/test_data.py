import pytest

from meguca import data
from meguca import exceptions


class TestDataStore():
    def test_getitem_with_existing_item(self):
        ins = data.DataStore()
        ins.update({'a': '1'})

        assert ins['a'] == '1'

    def test_getitem_with_non_existing_item(self):
        ins = data.DataStore()
        ins.update({'a': '1'})

        with pytest.raises(exceptions.NotFound):
            ins['b']

    def test_getitem_with_not_yet_existing_item(self):
        ins = data.DataStore(raise_notyetexist=True)
        ins.update({'a': '1'})

        with pytest.raises(exceptions.NotYetExist):
            ins['b']

    def test_toggle_raise_notyetexist(self):
        ins = data.DataStore()

        ins.raise_notyetexist = True

        assert ins.raise_notyetexist == True
