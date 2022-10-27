"""General API tests"""
import pytest

import datapane as dp

from .common import deletable, gen_name

# pytestmark = pytest.mark.usefixtures("dp_login")
pytestmark = pytest.mark.skip("LeagacyApp tests disabled")


def test_login_fixture():
    """Test that the fixture-based login, using config object, works"""
    dp.ping()


@pytest.mark.org
def test_environment():
    test_env_value = {"FOO": "BAR"}

    # create environment
    with deletable(dp.Environment.create(name=gen_name(), environment=test_env_value)) as v1:
        assert v1.environment == test_env_value
