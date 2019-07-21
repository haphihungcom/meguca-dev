import os

import pytest


@pytest.fixture
def mock_templates():
    """Create mock dispatch templates.
    """

    existing_templates = []

    def gen_mock_templates(templates={'test.txt': ''}):
        for name, text in templates.items():
            with open(name, 'w') as f:
                f.write(text)
                existing_templates.append(name)

    yield gen_mock_templates

    for name in existing_templates:
        with open(name, 'w') as f:
            os.remove(name)
