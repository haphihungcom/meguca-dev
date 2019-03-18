"""Create dispatches based on templates and upload them.
"""


import logging

from meguca import plugin_categories
from meguca.plugins.src.dispatch_updater import dispatch_renderer


logger = logging.getLogger(__name__)


class DispatchUpdater(plugin_categories.View):
    def prepare(self, ns_site):
        self.renderer = dispatch_renderer.Renderer(self.plg_config['general']['template_dir_path'],
                                                   self.plg_config['custom_bbcode_tags'])
        self.dispatches = self.plg_config['dispatches']
        self.ns_site = ns_site

    def run(self, data):
        self.renderer.data = data.get_bare_obj()

        for name, info in self.dispatches.items():
            content = self.renderer.render_dispatch(name)
            self.update_dispatch(info, content)

            logger.info('Updated dispatch "%s"', name)

    def update_dispatch(self, info, content):
        """Update dispatch.

        Args:
            info (dict): Dispatch information.
            content (str): New content.
        """

        subcategory_name = "subcategory-{}".format(info['category'])
        params = {'edit': str(info['id']),
                  'category': str(info['category']),
                  subcategory_name: str(info['sub_category']),
                  'dname': info['title'],
                  'message': content,
                  'submitbutton': '1'}

        self.ns_site.execute('lodge_dispatch', params)