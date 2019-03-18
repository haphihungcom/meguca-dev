"""This module contains plugin category classes for plugins to inherit.
"""


from yapsy import IPlugin


class MegucaPlugin(IPlugin.IPlugin):
    """Base plugin class."""

    # Plugin-specific configurations
    plg_config = None


class Service(MegucaPlugin):
    """Base class for plugins that provide services
    such as API wrappers, database interfaces,...
    """

    def get(self):
        """Return an instance of the service."""

        raise NotImplementedError


class StandardPlugin(MegucaPlugin):
    """Base class for standard plugins."""

    def run(self):
        """Entry method."""

        raise NotImplementedError

    def prepare(self):
        """Entry method for prime run."""


class Collector(StandardPlugin):
    """Base class for plugins that collect data.
    Implement run() as entry point for normal run
    and start() as entry point for initialization (optional).
    run() and prepare() needs to return a dictionary which contains
    data you want to return.
    """


class Stat(StandardPlugin):
    """Base class for plugins that calculate and return data.
    Implement run() as entry point for normal run
    and start() as entry point for initialization (optional).
    run() and prepare() needs to return a dictionary which contains
    data you want to return.
    """


class View(StandardPlugin):
    """Base class for plugins that output data.
    Implement run() as entry point for normal run
    and prepare() as entry point for initialization (optional).
    """
