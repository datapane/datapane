import random
import string
import uuid
from contextlib import contextmanager
from typing import ContextManager, TypeVar

import pandas as pd
import pytest

from datapane.client.api import BEObjectRef, HTTPError, Report


code: str = """
print("hello world")
"""


def gen_df(dim: int = 4) -> pd.DataFrame:
    axis = [i for i in range(0, dim)]
    data = {"x": axis, "y": axis}
    return pd.DataFrame.from_dict(data)


def gen_name(n=10):
    return f"Test_{''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=n))}"


def gen_headline() -> str:
    return f"test - {uuid.uuid4().hex}"


def gen_title() -> str:
    return f"test - {uuid.uuid4().hex}"


U = TypeVar("U", bound=BEObjectRef)


@contextmanager
def deletable(x: U) -> ContextManager[U]:
    try:
        yield x
    finally:
        x.delete()
        with pytest.raises(HTTPError) as _:
            # TODO - fixme
            if isinstance(x, Report):
                _ = Report.get(x.name)
            else:
                _ = x.__class__(x.name)
