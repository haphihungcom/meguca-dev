import collections

from meguca import exceptions


class DataStore(collections.UserDict):
    """Shared data dictionary for plugins to use and store data."""

    def __init__(self, raise_notyetexist=False, *args, **kwargs):
        self._raise_notyetexist = raise_notyetexist
        super().__init__(*args, **kwargs)

    @property
    def raise_notyetexist(self):
        return self._raise_notyetexist

    @raise_notyetexist.setter
    def raise_notyetexist(self, toggle):
        self._raise_notyetexist = toggle

    def __getitem__(self, key):
        """Index the object.

        Args:
            key (int|str): Index number or key.

        Raises:
            exceptions.NotFound: Raise if cannot index object.
            exceptions.NotYetExist: Raise if cannot index object when raise_notyetexist is True.

        Returns:
            Result of the indexing.
        """

        if key not in self.data:
            if self._raise_notyetexist:
                raise exceptions.NotYetExist(key)
            else:
                raise exceptions.NotFound(key)

        return self.data[key]
