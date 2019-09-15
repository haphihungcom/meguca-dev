"""Custom BBcode tags.
"""

import toml

from meguca.plugins.src.dispatch_updater import BBCode
from meguca.dispatch_templates.bbcode import utils


@BBCode.register('url')
class Url():
    def format(self, tag_name, value, options, parent, context):
        url = utils.get_url(options['url'],
                            context['urls'],
                            context['dispatch_info'])
        return '[url={}][color=#ff9900]{}[/color][/url]'.format(url, value)


@BBCode.register('raw_url')
class RawUrl():
    def format(self, tag_name, value, options, parent, context):
        url = utils.get_url(options['raw_url'],
                            context['urls'],
                            context['dispatch_info'])
        return '[url={}]{}[/url]'.format(url, value)


@BBCode.register('ref')
class Ref():
    def format(self, tag_name, value, options, parent, context):
        if '[*]' in value:
            return ('[font=Avenir, Segoe UI, sans-serif][size=120][color=#019aed][b]References: [/b]'
                    '[/color][/size][/font][list]{}[/list]').format(value)
        else:
            return ('[font=Avenir, Segoe UI, sans-serif][size=120][color=#019aed][b]Reference: [/b]'
                    '[/color]{}[/size][/font]').format(value)


@BBCode.register('law')
class Law():
    def __init__(self):
        path = self.config['laws_config_path']
        laws = toml.load(path)['laws']
        self.names_lut = utils.build_names_lut(laws)

    def format(self, tag_name, value, options, parent, context):
        url = utils.get_laws_url(value, self.config,
                                 self.names_lut, context['dispatch_info'])
        return '[url={}][color=#ff9900]{}[/color][/url]'.format(url, value)