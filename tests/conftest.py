import os
import configparser
from unittest import mock

import toml
import pytest


@pytest.fixture
def mock_plg():
    """A mock plugin with standard entry methods and config.
    It behaves like a real plugin."""

    def gen_mock_plg(name='Test', id='test', service=False):
        def stub_run():
            return {name: 'Test'}

        def stub_prepare():
            return {name: 'TestPrep'}

        def stub_dry_run():
            return {name: 'TestDry'}

        if service:
            def stub_get():
                return 'TestGet'
            mock_plg_obj = mock.Mock(get=stub_get)
        else:
            mock_plg_obj = mock.Mock(run=stub_run, prepare=stub_prepare, dry_run=stub_dry_run)

        config = configparser.ConfigParser()
        config['Core'] = {'ConfigFile': 'TestFile', 'Id': id}

        mock_plg = mock.Mock(plugin_object=mock_plg_obj,
                             details=config)
        type(mock_plg).name = mock.PropertyMock(return_value=name)

        return mock_plg

    return gen_mock_plg


@pytest.fixture
def toml_files():
    """Generate TOML config files for testing."""

    existing_files = []

    def gen_toml_files(files={}):
        for name, config in files.items():
            with open(name, 'w') as f:
                toml.dump(config, f)
                existing_files.append(name)

    yield gen_toml_files

    for name in existing_files:
        os.remove(name)


@pytest.fixture
def text_files():
    """Create text files for testing.
    """

    existing_files = []

    def gen_mock_files(files={'test.txt': ''}):
        for name, text in files.items():
            with open(name, 'w') as f:
                f.write(text)
                existing_files.append(name)

    yield gen_mock_files

    for name in existing_files:
        with open(name, 'w') as f:
            os.remove(name)
