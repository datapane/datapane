from __future__ import annotations

import secrets

from .base import BaseBlock, BlockId


def gen_name() -> str:
    """Return a (safe) name for use in a Block"""
    return f"id-{secrets.token_urlsafe(8)}"


class Empty(BaseBlock):
    """
    An empty block that can be updated / replaced later

    Args:
        name: A unique name for the block to reference when updating the report
    """

    _tag = "Empty"

    def __init__(self, name: BlockId):
        super().__init__(name=name)
