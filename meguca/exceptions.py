class Meguca(Exception):
    """Base exception for all Meguca-related exceptions."""


class PluginError(Meguca):
    """Base exception for plugin-related exceptions."""


class NotYetExist(PluginError):
    """Raise if get a non-yet-exist item from entry-point method's parameters."""


class NotFound(PluginError):
    """Raise if get a non-existent item from entry-point method's parameters."""