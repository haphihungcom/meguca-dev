from meguca import exceptions


class NSSiteError(exceptions.Meguca):
    """Base exception for all NS Site-related errors."""
    pass


class NSSiteHTTPError(exceptions.Meguca):
    """Raise if HTTP status code is not 200."""
    pass

class NSSiteSecurityError(NSSiteError):
    """Raise if a security check failure occurs."""
    pass


class NSSiteNotFound(NSSiteError):
    """Raise if NationStates cannot find something."""
    pass