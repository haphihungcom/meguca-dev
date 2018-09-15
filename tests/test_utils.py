import os
import configparser

import pytest

from meguca import utils


class TestLoadConfig():
    @pytest.fixture(scope='class')
    def setup_config_file(self):
        config = configparser.ConfigParser()

        config['Example'] = {'Example': '0'}

        with open('tests/test_config.ini', 'w') as f:
            config.write(f)

        yield 0

        os.remove('tests/test_config.ini')

    def test_load_config_from_ini(self, setup_config_file):
        config = utils.load_config('tests/test_config.ini')

        assert config['Example']['example'] == '0'