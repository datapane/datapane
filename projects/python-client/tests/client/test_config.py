# Test values which do not match the defaults
TEST_SERVER = "https://cloud.example.com"
TEST_TOKEN = "test_token"
TEST_USER = "user@example.com"
TEST_SESSION_ID = "test_session"


import pytest

from datapane.client import config as config_module
from datapane.client.config import Config


@pytest.fixture
def write_config():
    ini_path = config_module.CONFIG_PATH

    def write(content: str, path=ini_path) -> None:
        path.write_text(strip_indent(content))

    return write


def strip_indent(line: str) -> str:
    """
    Improve legibility of multi-line test strings by stripping indentation
    """
    lines = line.strip("\n").splitlines()
    indent = len(lines[0]) - len(lines[0].lstrip(" "))
    return "\n".join(line[indent:] for line in lines)


@pytest.mark.skip_setup
def test_config__load_legacy_yaml__loads_successfully(write_config):
    yaml_sample = f"""
    # server API address
    server: {TEST_SERVER}
    # API token - copy and paste from https://server/settings/
    token: {TEST_TOKEN}
    email: {TEST_USER}
    session_id: {TEST_SESSION_ID}
    version: 1
    completed_action: false
    """
    yml_path = config_module.APP_DIR / config_module.LEGACY_CONFIG_FILENAME
    write_config(yaml_sample, path=yml_path)
    config = Config.load()
    assert config.server == TEST_SERVER
    assert config.token == TEST_TOKEN
    assert config.email == TEST_USER
    assert config.session_id == TEST_SESSION_ID
    assert config.version == 6
