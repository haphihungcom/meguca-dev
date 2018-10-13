class Meguca(Exception):
    """Base exception for all Meguca-related exceptions."""


class GeneralError(Meguca):
    """Raise if a general error happens."""


class PluginError(Meguca):
    """Base exception for plugin management-related exceptions."""


class NotFound(PluginError):
    """Raise if get a non-existent item from entry-point method's parameters."""

    def __init__(self, key):
        self.non_existent_key = key

    def __str__(self):
        return self.non_existent_key


class NotYetExist(NotFound):
    """Raise if get a non-yet-exist item from entry-point method's parameters."""
