import os
import toml

import pytest

from meguca import utils


class TestLoadConfig():
    @pytest.fixture(scope='class')
    def setup_config_file(self):
        config = {'Example': {'ExampleKey': 'ExampleVal'}}

        with open('tests/test_config.toml', 'w') as f:
            toml.dump(config, f)

        yield 0

        os.remove('tests/test_config.toml')

    def test_load_config_from_toml_file(self, setup_config_file):
        config = utils.load_config('tests/test_config.toml')

        assert config['Example']['ExampleKey'] == 'ExampleVal'