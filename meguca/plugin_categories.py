"""This module contains plugin category classes for plugins to inherit.
"""


from yapsy import IPlugin


class MegucaPlugin(IPlugin.IPlugin):
    """Base plugin class."""

    # Plugin-specific configurations
    plg_config = None
    logger = None


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


class Collector(StandardPlugin):
    """Base class for plugins that collect data.
    Implement run() as entry point for normal run
    and prime_run() as entry point for prime run (optional).
    run() and prime_run() needs to return a dictionary which contains
    data you want to return.
    """

    def prime_run(self):
        """Entry method for prime run."""


class Stat(StandardPlugin):
    """Base class for plugins that calculate and return data.
    Implement run() as entry point.
    run() needs to return a dictionary which contains data
    you want to return.
    """


class View(StandardPlugin):
    """Base class for plugins that output data.
    Implement run() as entry point.
    """
