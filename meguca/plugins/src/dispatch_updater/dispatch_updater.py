"""Create dispatches based on templates and upload them.
"""


import logging
import time

import toml

from meguca import plugin_categories
from meguca.plugins.src.dispatch_updater import dispatch_renderer
from meguca.plugins.src.dispatch_updater import utils


logger = logging.getLogger(__name__)


class DispatchUpdater(plugin_categories.View):
    def prepare(self, ns_site, data):
        self.renderer = dispatch_renderer.Renderer(self.plg_config['general']['template_dir_path'],
                                                   self.plg_config['general']['filters_path'],
                                                   self.plg_config['general']['bb_path'],
                                                   self.plg_config['general']['custom_vars_path'],
                                                   self.plg_config['general']['template_file_ext'],
                                                   self.plg_config)
        self.ns_site = ns_site
        self.dispatches = utils.load_dispatch_config(self.plg_config['general']['dispatch_config_path'])

        self.id_store = utils.IDStore(self.plg_config['general']['id_store_path'])
        self.id_store.load_from_json()
        self.id_store.load_from_dispatch_config(self.dispatches)

        self.data = data
        self.update_ctx()

    def update_ctx(self):
        self.renderer.update_data(self.data)

    def run(self):
        self.update_ctx()
        self.update_all_dispatches()
        self.id_store.save()

    def dry_run(self):
        self.update_ctx()

        if not self.plg_config['dry_run']['dispatches']:
            self.update_all_dispatches()
        else:
            for name in self.plg_config['dry_run']['dispatches']:
                self.update_dispatch(name, self.dispatches[name])

        self.id_store.save()

    def update_all_dispatches(self):
        """Update all dispatches.
        """

        if not self.dispatches:
            logger.warning('No dispatch was configured')
        else:
            for name, info in self.dispatches.items():
                self.update_dispatch(name, info)

    def add_dispatch_id(self, html, name):
        """Add new dispatch ID.

        Args:
            html (str): HTML from response.
            name (str): Dispatch file name.
        """

        dispatch_id = utils.get_new_dispatch_id(html)
        self.id_store[name] = dispatch_id
        logger.debug('Added ID "%d" of dispatch "%s"',
                     dispatch_id, name)

    def update_dispatch(self, name, info):
        """Update dispatch. Update dispatch ID if needed.

        Args:
            name (str): Dispatch file name.
            info (dict): Dispatch information.
        """

        text = self.renderer.render(name)

        if name not in self.id_store:
            html = self.upload_dispatch(info, text)
            self.add_dispatch_id(html, name)
        else:
            self.upload_dispatch(info, text, str(self.id_store[name]))

        logger.info('Updated dispatch "%s"', name)

    def upload_dispatch(self, info, text, edit_id=None):
        """Upload dispatch.

        Args:
            info (dict): Dispatch information.
            text (str): Text to upload.
            edit_id (str|None): Dispatch ID.
        """

        subcategory_name = "subcategory-{}".format(info['category'])
        params = {'edit': edit_id,
                  'category': str(info['category']),
                  subcategory_name: str(info['sub_category']),
                  'dname': info['title'],
                  'message': text,
                  'submitbutton': '1'}

        return self.ns_site.execute('lodge_dispatch', params)

