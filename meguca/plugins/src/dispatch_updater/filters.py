"""Custom template filters."""


def nation(name, modifier=None):
    """Enclose nation name with [nation][/nation] tag.

    Args:
        name (str): Nation name.
        mode (str, optional): Defaults to None. Modifier (short, noflag, noname).

    Returns:
        str: [nation=modifier]nation name[/nation]
    """

    if modifier is None:
        return '[nation]{}[/nation]'.format(name)

    return '[nation={}]{}[/nation]'.format(modifier, name)


def region(name):
    """Enclose region name with [region][/region] tag.

    Args:
        name (str): Region name.

    Returns:
        str: [region]region name[/region]
    """

    return '[region]{}[/region]'.format(name)
