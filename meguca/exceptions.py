class Meguca(Exception):
    """Base exception for all Meguca-related exceptions"""


class PluginError(Meguca):
    """Base exception for plugin-related exceptions"""


class NotFound(PluginError):
    """Raise if get a non-existent key from a hook"""


class NSAPIError(Meguca):
    """Base exception for NS API-related exceptions"""


class NSAPIRateLimitError(NSAPIError):
    """Raise if API rate limit was exceeded"""


class NSAPIReqError(NSAPIError):
    """Raise if there is an error in the API request
    i.e non-existent regions, incorrect shard names, parameters,...
    """


class NSAPIAuthError(NSAPIError):
    """Raise if there is an error during authentication
    for private calls
    i.e incorrect password
    """