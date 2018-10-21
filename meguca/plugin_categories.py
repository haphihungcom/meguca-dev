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
        """Return service objects."""

        raise NotImplementedError


class StandardPlugin(MegucaPlugin):
    """Base class for standard plugins."""

    def run(self):
        """Entry point method of all standard plugins."""

        raise NotImplementedError


class Collector(StandardPlugin):
    """Base class for plugins that collect data.
    Implement run() as entry point for normal run mode
    and prime_run() as entry point for prime run mode.
    run() and prime_run() needs to return a dict which contains
    data you want to return. The key names in the dict will be used
    as identifiers of the data you return. These identifiers
    will be used by Meguca and other plugins to get the data
    created by this plugin.
    """

    def prime_run(self):
        """Entry point method for prime run."""

        raise NotImplementedError


class Stat(StandardPlugin):
    """Base class for plugins that calculate and return stats
    Implement run() as entry point.
    run() needs to return a dict contains stats you want to
    return. The dict's key names will be used as identifiers
    of the stats you return. These identifiers will be used by
    Meguca and other plugins to access the stats created
    by this plugin.
    """


class View(StandardPlugin):
    """Base class for plugins that output data.
    Implement run() as entry point.
    """