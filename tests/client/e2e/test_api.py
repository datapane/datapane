import pytest

import datapane as dp

from .common import deletable, gen_name

pytestmark = pytest.mark.usefixtures("dp_login")


@pytest.mark.org
def test_variable():
    test_value = "test_var_value"

    # create secret variable
    with deletable(dp.Variable.create(name=gen_name(), value=test_value)) as v1:
        assert v1.value == test_value
