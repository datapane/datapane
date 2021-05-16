import random
import string
import uuid
from contextlib import contextmanager
from typing import ContextManager

import pytest
import stringcase

from datapane.client.api import HTTPError
from datapane.client.api.dp_object import U
from datapane.client.api.templates import gen_df  # noqa

code: str = """
print("hello world")
"""


def gen_name(n=10):
    return f"Test {''.join(random.choices(string.ascii_lowercase, k=n))}"


def check_name(obj, orig_name: str):
    assert obj.title == orig_name
    assert obj.name == stringcase.spinalcase(orig_name)


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
