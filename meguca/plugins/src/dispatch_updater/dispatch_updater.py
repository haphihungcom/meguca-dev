"""Create dispatches based on templates and upload them.
"""


import logging

from meguca import plugin_categories
from meguca.plugins.src.dispatch_updater import dispatch_renderer


logger = logging.getLogger(__name__)


class DispatchUpdater(plugin_categories.View):
    def prepare(self, ns_site):
        self.renderer = dispatch_renderer.Renderer(self.plg_config['general']['template_dir_path'],
                                                   self.plg_config['general']['filters_path'],
                                                   self.plg_config['general']['bb_path'],
                                                   self.plg_config['general']['custom_vars_path'],
                                                   self.plg_config)
        self.dispatches = self.plg_config['dispatches']
        self.ns_site = ns_site

    def run(self, data):
        self.renderer.update_data(data.get_bare_obj())

        template_ext = self.plg_config['general']['template_file_ext']
        for name, info in self.dispatches.items():
            template_path = '{}.{}'.format(name, template_ext)
            text = self.renderer.render(template_path)
            self.update_dispatch(info, text)
            logger.info('Updated dispatch "%s"', name)

    def update_dispatch(self, info, text):
        """Update dispatch.

        Args:
            info (dict): Dispatch information.
            text (str): Text.
        """

        subcategory_name = "subcategory-{}".format(info['category'])
        params = {'edit': str(info['id']),
                  'category': str(info['category']),
                  subcategory_name: str(info['sub_category']),
                  'dname': info['title'],
                  'message': text,
                  'submitbutton': '1'}

        self.ns_site.execute('lodge_dispatch', params)