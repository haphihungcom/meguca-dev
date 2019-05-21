"""Custom BBcode tags.
"""

from meguca.dispatch_templates.bbcode import utils


def url(tag_name, value, options, parent, context):
    url = utils.get_url(options['url'],
                        context['custom_vars']['urls'],
                        context['config']['dispatches'])
    return '[url={}][color=#ff9900]{}[/color][/url]'.format(url, value)


def raw_url(tag_name, value, options, parent, context):
    url = utils.get_url(options['raw_url'],
                        context['custom_vars']['urls'],
                        context['config']['dispatches'])
    return '[url={}]{}[/url]'.format(url, value)


def ref(tag_name, value, options, parent, context):
    if '[*]' in value:
        return ('[font=Segoe UI, Helvetica, sans-serif][size=120][color=1089e6][b]Reference: [/b]'
                '[/color][/size][/font][list]{}[/list]').format(value)
    else:
        return ('[font=Segoe UI, Helvetica, sans-serif][size=120][color=1089e6][b]Reference: [/b]'
                '[/color][/size][/font]{}').format(value)