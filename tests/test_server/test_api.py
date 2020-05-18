import pytest

from datapane.client import api

from .common import gen_name

pytestmark = pytest.mark.usefixtures("dp_login")


def test_variable():
    variable = None
    test_value = "test_var_value"
    try:
        # create secret variable
        variable = api.Variable.add(name=gen_name(), value=test_value)
        assert variable.value == test_value

    finally:
        if variable:
            variable.delete()
            with pytest.raises(api.HTTPError) as _:
                _ = api.Variable(variable.name)
