"""Create dispatches based on templates and upload them.
"""


import logging

from meguca import plugin_categories
from meguca.plugins.src.dispatch_updater import dispatch_renderer


logger = logging.getLogger(__name__)


class DispatchUpdater(plugin_categories.View):
    def run(self, data, ns_site):
        renderer = dispatch_renderer.Renderer(self.plg_config['General']['TemplateDirectory'],
                                              self.plg_config['CustomBBCodeTags'], data)
        self.ns_site = ns_site

        dispatches = self.plg_config['Dispatches']
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

        subcategory_name = "subcategory-{}".format(info['Category'])
        params = {'edit': str(info['Id']),
                  'category': str(info['Category']),
                  subcategory_name: str(info['Subcategory']),
                  'dname': info['Title'],
                  'message': content,
                  'submitbutton': '1'}

        self.ns_site.execute('lodge_dispatch', params)