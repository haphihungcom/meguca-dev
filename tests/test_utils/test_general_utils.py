import os
import configparser

import pytest

from meguca.utils import general_utils


class TestLoadConfig():
    @pytest.fixture(scope='class')
    def setup_config_file(self):
        config = configparser.ConfigParser()
        config.optionxform = str

        config['Example'] = {'Example': '0'}

        with open('tests/test_config.ini', 'w') as f:
            config.write(f)

        yield 0

        os.remove('tests/test_config.ini')

    def test_load_config_from_ini(self, setup_config_file):
        config = general_utils.load_config('tests/test_config.ini')

        assert config['Example']['Example'] == '0'