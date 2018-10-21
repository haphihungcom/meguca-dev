from meguca import plugin_categories


class DelegateStats(plugin_categories.Stat):
    def run(self, ns_api, data, config):
        incumbent_delegate = ns_api.get_region(config['Meguca']['General']['region'], 'delegate')
        delegate_ec = ns_api.get_nation(self.plg_config['Delegate']['Name'],
                                     'census',
                                     {'mode': 'score', 'scale': '66'})['CENSUS']['SCALE']['SCORE']

        return {'incumbent_delegate': incumbent_delegate,
                'delegate_ec': total_endocount}