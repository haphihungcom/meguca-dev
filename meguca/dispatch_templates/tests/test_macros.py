import pytest
import jinja2


TEMPLATE_DIR = 'meguca/dispatch_templates'
TEST_DIR = 'meguca/dispatch_templates/tests/'


class TestMacros():
    @pytest.fixture(scope='class')
    def env(self):
        template_loader = jinja2.FileSystemLoader(TEMPLATE_DIR)
        env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True)

        yield env

    def test_gen_header_no_urls(self, env):
        template = env.get_template('tests/gen_header_no_urls_test.txt')

        assert template.render() == open(TEST_DIR + 'gen_header_no_urls_expected.txt').read()

    def test_gen_header_with_urls(self, env):
        template = env.get_template('tests/gen_header_with_urls_test.txt')

        assert template.render() == open(TEST_DIR + 'gen_header_with_urls_expected.txt').read()

    def test_2rows_gen_header(self, env):
        template = env.get_template('tests/gen_2rows_header_test.txt')

        assert template.render() == open(TEST_DIR + 'gen_2rows_header_expected.txt').read()


