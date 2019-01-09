def key_val_format(key, val):
    """Get a key=value formatted parameter string."""

    return "{}={}".format(key, val)


def construct_url(params, url_beginning, param_delim, param_val_delim):
    """Construct the parameter part of a URL."""

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
