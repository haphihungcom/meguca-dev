from yapsy import IPlugin

class MegucaPlugin(IPlugin.IPlugin):
    """Base plugin class."""

    # Plugin-specific configurations
    plg_config = None
    logger = None

    def run(self):
        """Entry point method of all plugins."""

        raise NotImplementedError


class Collector(MegucaPlugin):
    """Base class for plugins that collect data.
    Implement run() as entry point for normal run mode
    and prime_run() as entry point for prime run mode.
    """

    def prime_run(self):
        """Entry point method for prime run."""

        raise NotImplementedError


class Stat(MegucaPlugin):
    """Base class for plugins that calculate and return stats
    Implement run() as entry point.
    run() needs to return a dict contains stats you want to
    return. The dict's key names will be used as identifiers
    of the stats you return. These identifiers will be used by
    Meguca and other plugins to access the stats created
    by this plugin.
    """

class View(MegucaPlugin):
    """Base class for plugins that output data.
    Implement run() as entry point.
    """