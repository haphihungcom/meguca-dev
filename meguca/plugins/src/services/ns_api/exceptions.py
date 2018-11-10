from meguca import exceptions

class NSAPIError(exceptions.Meguca):
    """Base exception for NS API-related exceptions"""


class NSAPIRateLimitError(NSAPIError):
    """Raise if API rate limit was exceeded"""


class NSAPIReqError(NSAPIError):
    """Raise if there is an error in the API request
    e.g non-existent regions, incorrect shard names, parameters,...
    """


class NSAPIAuthError(NSAPIError):
    """Raise if there is an error during authentication
    for private calls
    e.g incorrect password, invalid pin,...
    """