"""Create dispatches based on templates and upload them.
"""


import logging
import time

from meguca import plugin_categories
from meguca.plugins.src.dispatch_updater import dispatch_renderer


logger = logging.getLogger(__name__)


class DispatchUpdater(plugin_categories.View):
    def prepare(self, ns_site, data):
        self.renderer = dispatch_renderer.Renderer(self.plg_config['general']['template_dir_path'],
                                                   self.plg_config['general']['filters_path'],
                                                   self.plg_config['general']['bb_path'],
                                                   self.plg_config['general']['custom_vars_path'],
                                                   self.plg_config)
        self.renderer.update_data(data)
        self.dispatches = self.plg_config['dispatches']
        self.ns_site = ns_site

    def run(self, data):
        self.renderer.update_data(data)

        for name, info in self.dispatches.items():
            self.update_dispatch(name, info)

    def dry_run(self, data):
        for name in self.plg_config['dry_run']['dispatches']:
            self.update_dispatch(name, self.dispatches[name])

    def update_dispatch(self, name, info):
        """Update dispatch.

        Args:
            name (str): Dispatch file name.
            info (dict): Dispatch information.
        """
        template_ext = self.plg_config['general']['template_file_ext']
        template_path = '{}.{}'.format(name, template_ext)
        text = self.renderer.render(template_path, name)
        self.upload_dispatch(info, text)

        logger.info('Updated dispatch "%s"', name)

    def upload_dispatch(self, info, text):
        """Upload dispatch.

        Args:
            info (dict): Dispatch information.
            text (str): Text to upload.
        """

        subcategory_name = "subcategory-{}".format(info['category'])
        params = {'edit': str(info['id']),
                  'category': str(info['category']),
                  subcategory_name: str(info['sub_category']),
                  'dname': info['title'],
                  'message': text,
                  'submitbutton': '1'}

        self.ns_site.execute('lodge_dispatch', params)
