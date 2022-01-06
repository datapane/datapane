import secrets
import uuid
from contextlib import contextmanager
from typing import ContextManager

import pytest

from datapane.client.api import HTTPError
from datapane.client.api.dp_object import U
from datapane.client.api.builtins import gen_df, gen_plot  # noqa

code: str = """
print("hello world")
"""


def gen_name(prefix: str = ""):
    return f"Test {prefix} {secrets.token_hex(3)}"


def check_name(obj, orig_name: str):
    assert obj.name == orig_name


def gen_description() -> str:
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
