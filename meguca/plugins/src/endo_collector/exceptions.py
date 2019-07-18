from meguca import exceptions


class EndoCollectorError(exceptions.Meguca):
    """Base exceptions for Endo Collector's errors."""
    pass


class IllegalEndorsement(EndoCollectorError):
    """Raises if attempting to process illegal endorsements.
    E.g Endorsements on non-existent nations."""
    pass