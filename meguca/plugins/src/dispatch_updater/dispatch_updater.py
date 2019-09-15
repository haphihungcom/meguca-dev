"""Create dispatches based on templates and upload them.
"""


import logging
import time
import codecs

import toml

from meguca import plugin_categories
from meguca import exceptions
from meguca.plugins.src.dispatch_updater import dispatch_renderer
from meguca.plugins.src.dispatch_updater import utils


logger = logging.getLogger(__name__)

RESERVED_PLACEHOLDER = "[reserved]"


class DispatchUploader():
    """Dispatch Uploader"""

    def __init__(self, renderer, ns_site, id_store, dispatch_config):
        self.ns_site = ns_site
        self.renderer = renderer
        self.dispatch_config = dispatch_config
        self.id_store = id_store

    def create_dispatch(self, name):
        """Create a new dispatch.

        Args:
            name (str): Dispatch file name.

        Returns:
            str: HTML response.
        """

        html = self.post_dispatch(self.dispatch_config[name], RESERVED_PLACEHOLDER)
        logger.info('Created new dispatch "%s"', name)

        return html

    def update_dispatch(self, name):
        """Update dispatch.

        Args:
            name (str): Dispatch file name.
            config (dict): Dispatch configuration.
        """

        text = self.renderer.render(name)
        dispatch_id = self.id_store[name]
        dispatch_config = self.dispatch_config[name]

        self.post_dispatch(dispatch_config, text, dispatch_id)
        logger.info('Updated dispatch "%s"', name)

    def post_dispatch(self, config, text, edit_id=None):
        """Post dispatch.

        Args:
            config (dict): Dispatch configuration.
            text (str): Text to post.
            edit_id (int|None): Dispatch ID. Defaults to None.
        """

        subcategory_name = "subcategory-{}".format(config['category'])
        params = {'category': str(config['category']),
                  subcategory_name: str(config['sub_category']),
                  'dname': config['title'],
                  'message': text.encode('windows-1252'),
                  'submitbutton': '1'}

        if edit_id:
            params['edit'] = str(edit_id)

        #time.sleep(6)
        return self.ns_site.execute('lodge_dispatch', params)


class DispatchUpdater(plugin_categories.View):
    def prepare(self, ns_site, config, data):
        general_conf = self.plg_config.get('general', {})
        self.ns_site = ns_site

        self.dispatch_config = utils.load_dispatch_config(general_conf.get('dispatch_config_path', None))
        if not self.dispatch_config:
            raise exceptions.PluginError('No dispatch was configured')
        self.blacklist = general_conf.get('blacklist', [])

        dry_run_conf = self.plg_config.get('dry_run', {})
        self.dry_run_dispatches = dry_run_conf.get('dispatches', None)

        self.id_store = utils.IDStore(general_conf.get('id_store_path', None))
        self.id_store.load_from_json()
        self.id_store.load_from_dispatch_config(self.dispatch_config)

        renderer_conf = self.plg_config.get('renderer', {})
        self.renderer = dispatch_renderer.Renderer(renderer_conf)

        self.uploader = DispatchUploader(self.renderer, ns_site,
                                         self.id_store, self.dispatch_config)

        self.create_all_dispatches()
        self.id_store.save()

        self.config = config
        self.data = data

    def update_ctx(self):
        dispatch_info = utils.get_dispatch_info(self.dispatch_config,
                                                self.id_store)
        self.renderer.update_ctx(self.data, self.plg_config,
                                 self.config, dispatch_info)

    def run(self):
        self.update_ctx()
        self.update_all_dispatches()

    def dry_run(self):
        self.update_ctx()

        if not self.dry_run_dispatches:
            self.update_all_dispatches()
        else:
            self.update_dispatches(self.dry_run_dispatches)

    def get_allowed_dispatches(self):
        """Get non-blacklisted dispatches.

        Returns:
            list: Dispatch file names.
        """

        return [dispatch for dispatch in self.dispatch_config.keys()
                if dispatch not in self.blacklist]

    def update_all_dispatches(self):
        """Update all dispatches except blacklisted ones.
        """

        dispatches = self.get_allowed_dispatches()
        self.update_dispatches(dispatches)

    def update_dispatches(self, dispatches):
        """Update dispatches

        Args:
            dispatches (list): Dispatch file names.
        """

        for name in dispatches:
            self.uploader.update_dispatch(name)

    def create_all_dispatches(self):
        """Create all dispatches except blacklisted ones.
        """

        dispatches = self.get_allowed_dispatches()
        self.create_dispatches(dispatches)

    def create_dispatches(self, dispatches):
        """Create dispatches and add their ID.

        Args:
            dispatches (list): Dispatch file names.
        """

        for name in dispatches:
            if name not in self.id_store:
                html = self.uploader.create_dispatch(name)
                self.id_store.add_id_from_html(name, html)
