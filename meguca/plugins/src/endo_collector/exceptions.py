from meguca import exceptions


class EndoCollectorErrror(exceptions.Meguca):
    """Base exceptions for Endo Collector's errors."""
    pass


class IllegalEndorsement(EndoCollectorErrror):
    """Raises if attempting to process illegal endorsements.
    E.g Endorsements on non-existent nations."""
    pass