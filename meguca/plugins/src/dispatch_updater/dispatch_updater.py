"""Create dispatches based on templates and upload them.
"""


import logging

from meguca import plugin_categories
from meguca.plugins.src.dispatch_updater import dispatch_renderer


logger = logging.getLogger(__name__)


class DispatchUpdater(plugin_categories.View):
    def run(self, data, ns_site):
        renderer = dispatch_renderer.Renderer(self.plg_config['general']['template_dir_path'],
                                              self.plg_config['custom_bbcode_tags'], data.get_bare_obj())
        self.ns_site = ns_site

        dispatches = self.plg_config['dispatches']
        for name, info in dispatches.items():
            content = renderer.render_dispatch(name)
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