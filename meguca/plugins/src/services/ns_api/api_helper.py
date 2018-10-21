def key_val_format(key, val):
    """Get a key=value formatted parameter str

    :param key: Parameter's key
    :param val: Parameter's value

    :rtype: A str with key=value format
    """

    return "{}={}".format(key, val)


def construct_url(params, url_beginning, param_delim, param_val_delim):
    """Construct the parameter part of the URL
    :param params: A dict containing the parameters
    :param url_beginning: The beginning part of the request URL
    :param param_delim: Delimiter that separates parameters
    :param param_val_delim: Delimiter that separates values of a parameter

    :rtype: A URL str
    """

    url = url_beginning

    for param in params.items():
        if param[0] == "" or param[1] == "":
            continue

        param_name = param[0]

        if isinstance(param[1], list):
            param_value = param_val_delim.join(param[1])
        else:
            param_value = param[1]

        url += key_val_format(param_name, param_value)
        url += param_delim

    return url
