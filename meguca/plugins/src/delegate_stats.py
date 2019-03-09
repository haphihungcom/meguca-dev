import logging

from meguca import plugin_categories


logger = logging.getLogger(__name__)


class DelegateStats(plugin_categories.Stat):
    def run(self, ns_api, config):
        incumbent_delegate = ns_api.get_region(config['meguca']['general']['region'], 'delegate')['DELEGATE']
        delegate_ec = ns_api.get_nation(self.plg_config['delegate']['name'],
                                        'census',
                                        {'mode': 'score', 'scale': '66'})['CENSUS']['SCALE']['SCORE']

        result =  {'incumbent_delegate': incumbent_delegate,
                   'delegate_ec': int(float(delegate_ec))}

        logger.debug('Delegate stats generated: %r', result)

        return result