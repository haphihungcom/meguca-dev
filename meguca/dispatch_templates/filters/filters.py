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


def gen_list(input_list, delimiter=', ', start_tag='[nation]', end_tag='[/nation]'):
    """Generate a text list with each item separated by a delimiter.
    E.g [nation]nation1[/nation], [nation]nation2[/nation], [nation]nation3[/nation]

    Args:
        input_list (list): List.
        delimiter (str, optional): Delimiter. Defaults to ', '.
        start_tag (str, optional): Start tag to format an item. Defaults to '[nation]'.
        end_tag (str, optional): End tag to format an item. Defaults to '[/nation].

    Returns:
        str: A text list.
    """

    result = delimiter.join(["{}{}{}".format(start_tag, item, end_tag) for item in input_list])

    return result


def gen_table_tags(input_list, column_num=5, start_tag='[nation]', end_tag='[/nation]'):
    """Generate table tags ([tr][td][/td][/tr]) for tables.
    E.g. [tr][td]nation1[/td][td]nation2[/td][/tr]

    Args:
        input_list (list): List.
        column_num (str, optional): Number of columns. Defaults to 5.
        start_tag (str, optional): Start tag to format a cell. Defaults to '[p][nation]'.
        end_tag (str, optional): End tag to format a cell. Defaults to '[/nation][/p].
    """

    result = ""

    for i in range(0, len(input_list), column_num):
        result += "[tr]"

        try:
            for j in range(i, i + column_num):
                result += "[td]{}{}{}[/td]".format(start_tag, input_list[j], end_tag)
        except(IndexError):
            pass

        result += "[/tr]"

    return result

