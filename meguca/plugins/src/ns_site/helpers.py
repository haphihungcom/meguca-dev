"""Helper function for NS Site.
"""

import bs4

from meguca.plugins.src.ns_site import exceptions


def handle_errors(resp):
        """Handling errors if a request returns them.

        Args:
            resp (requests.Response): Respond.

        Raises:
            Refer to NS Site exceptions for the exception each type of errors may raise.
        """

        if resp.status_code != 200:
            raise exceptions.NSSiteHTTPError("""A HTTP error occured when connecting to NationStates website.
                                             HTTP status code: {}""".format(resp.status_code))

        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        error_elem = soup.find(name='p', attrs={'class': 'error'})

        if error_elem is None:
            return
        else:
            error = error_elem.string

        if "security check" in error:
            raise exceptions.NSSiteSecurityError("Security check failed. Please don't login into the "
                                                 "host nation elsewhere while the software is running.")
        elif "does not exist" in error:
            raise exceptions.NSSiteNotFound('The requested page does not exist.')
        else:
            raise exceptions.NSSiteError(error)


def get_localid(html_text):
    """Extract localid from HTML.

    Args:
        html_text (str): HTML text of respond.

    Returns:
        str: localid.
    """

    soup = bs4.BeautifulSoup(html_text, 'html.parser')
    return soup.find(name='input', attrs={'name': 'localid'})['value']