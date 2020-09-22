import random
import string
import uuid
from contextlib import contextmanager
from typing import ContextManager

import pandas as pd
import pytest

from datapane.client.api import HTTPError
from datapane.client.api.dp_object import U

code: str = """
print("hello world")
"""


def gen_df(n: int = 4) -> pd.DataFrame:
    """Build a (reprodcible) df of 2 cols and n rows"""
    axis = [i for i in range(0, n)]
    data = {"x": axis, "y": axis}
    return pd.DataFrame.from_dict(data)


def gen_name(n=10):
    return f"Test_{''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=n))}"


def gen_description() -> str:
    return f"test - {uuid.uuid4().hex}"


def gen_title() -> str:
    return f"test - {uuid.uuid4().hex}"


@contextmanager
def deletable(x: U) -> ContextManager[U]:
    try:
        yield x
    finally:
        x.delete()
        with pytest.raises(HTTPError) as _:
            try:
                _ = x.__class__.get(x.name)
            except AttributeError:
                _ = x.__class__.by_id(x.id)
