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


def gen_list(input_list, delimiter=', ', tag='nation', tag_modifier=None):
    """Generate a text list with each item separated by a delimiter.
    E.g [nation]nation1[/nation], [nation]nation2[/nation], [nation]nation3[/nation]

    Args:
        input_list (list): List.
        delimiter (str, optional): Delimiter. Defaults to ', '.
        tag (str, optional): Tag to wrap around an item. Defaults to 'nation'.
        tag_modifier (str, optional): Tag modifier. Defaults to None.

    Returns:
        str: A text list.
    """

    result = ""

    if tag is None:
            result += delimiter.join(input_list)
    elif tag_modifier is None:
        result = delimiter.join(["[{}]{}[/{}]".format(tag, item, tag) for item in input_list])
    else:
        result = delimiter.join(["[{}={}]{}[/{}]".format(tag, tag_modifier, item, tag) for item in input_list])

    return result
