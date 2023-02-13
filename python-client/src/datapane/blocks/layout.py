from __future__ import annotations

import enum
import typing as t
from collections import deque
from functools import reduce

from glom import glom

from datapane.client import DPClientError

from .base import BaseElement, BlockId, BlockList, BlockOrPrimitive, wrap_block
from .function import Empty, gen_name

if t.TYPE_CHECKING:
    from typing_extensions import Self

    from datapane.blocks import Block

    from .base import VV


class SelectType(enum.Enum):
    DROPDOWN = "dropdown"
    TABS = "tabs"


class ContainerBlock(BaseElement):
    """
    Abstract Block that supports nested/contained blocks
     - represents a subtree in the document
    """

    blocks: BlockList

    def __init__(self, *arg_blocks: BlockOrPrimitive, blocks: t.List[BlockOrPrimitive] = None, **kwargs):
        self.blocks = blocks or list(arg_blocks)
        if len(self.blocks) == 0:
            raise DPClientError(f"Can't create {self._tag} with 0 entries")
        self.blocks = [wrap_block(b) for b in self.blocks]

        super().__init__(**kwargs)

    def __iter__(self):
        return BlockListIterator(self.blocks.__iter__())

    def __add__(self, other: Self) -> Self:
        self.blocks.extend(other.blocks)
        return self

    def __and__(self, other: Self) -> Self:
        self.blocks.extend(other.blocks)
        return self

    def __copy__(self) -> Self:
        inst = super().__copy__()
        inst.blocks = self.blocks.copy()
        return inst

    @classmethod
    def empty(cls) -> Self:
        return cls(blocks=[Empty(gen_name())])

    def traverse(self, visitor: VV) -> VV:
        # perform a depth-first traversal of the contained blocks
        return reduce(lambda _visitor, block: block.accept(_visitor), self.blocks, visitor)


class Page(ContainerBlock):
    """
    Page objects take a list of blocks which make up the Page.
    This is included for backwards-compatability, and can be replaced by using Selects going forwards

    ..note:: You can pass ordinary Blocks to a page, e.g. Plots or DataTables.
      Additionally, if a Python object is passed, e.g. a Dataframe, Datapane will attempt to convert it automatically.
    """

    # BC-only helper - converted into a Select + Group within the post-XML processor
    _tag = "_Page"

    def __init__(
        self,
        *arg_blocks: BlockOrPrimitive,
        blocks: t.List[BlockOrPrimitive] = None,
        title: str = None,
        name: BlockId = None,
    ):
        """
        Args:
            *arg_blocks: Blocks to add to Page
            blocks: Allows providing the report blocks as a single list
            title: The page title (optional)
            name: A unique id for the Page to aid querying (optional)

        ..tip:: Page can be passed using either arg parameters or the `blocks` kwarg, e.g.
          `dp.Page(group, select)` or `dp.Group(blocks=[group, select])`
        """
        self.title = title
        super().__init__(*arg_blocks, blocks=blocks, label=title, name=name)

        if any(isinstance(b, Page) for b in self.blocks):
            raise DPClientError("Nested pages not supported, please use Selects and Groups")


class Select(ContainerBlock):
    """
    Selects act as a container that holds a list of nested Blocks objects, such
    as Tables, Plots, etc.. - but only one may be __visible__, or "selected", at once.

    The user can choose which nested object to view dynamically using either tabs or a dropdown.

    ..note:: Select expects a list of Blocks, e.g. a Plot or Table, but also including Select or Groups themselves,
      but if a Python object is passed, e.g. a Dataframe, Datapane will attempt to convert it automatically.

    """

    _tag = "Select"

    def __init__(
        self,
        *arg_blocks: BlockOrPrimitive,
        blocks: t.List[BlockOrPrimitive] = None,
        type: t.Optional[SelectType] = None,
        name: BlockId = None,
        label: str = None,
    ):
        """
        Args:
            *arg_blocks: Page to add to report
            blocks: Allows providing the report blocks as a single list
            type: An instance of SelectType that indicates if the select should use tabs or a dropdown
            name: A unique id for the blocks to aid querying (optional)
            label: A label used when displaying the block (optional)

        ..tip:: Select can be passed using either arg parameters or the `blocks` kwarg, e.g.
          `dp.Select(table, plot, type=dp.SelectType.TABS)` or `dp.Select(blocks=[table, plot])`
        """
        _type = glom(type, "value", default=None)
        super().__init__(*arg_blocks, blocks=blocks, name=name, label=label, type=_type)
        if len(self.blocks) < 2:
            raise DPClientError("Can't create Select with less than 2 objects")


class Group(ContainerBlock):
    """
    Groups act as a container that holds a list of nested Blocks objects, such
    as Tables, Plots, etc.. - they may even hold Group themselves recursively.

    Group are used to provide a grouping for blocks can have layout options applied to them

    ..note:: Group expects a list of Blocks, e.g. a Plot or Table, but also including Select or Groups themselves,
      but if a Python object is passed, e.g. a Dataframe, Datapane will attempt to convert it automatically.
    """

    _tag = "Group"

    def __init__(
        self,
        *arg_blocks: BlockOrPrimitive,
        blocks: t.List[BlockOrPrimitive] = None,
        name: BlockId = None,
        label: t.Optional[str] = None,
        columns: int = 1,
    ):
        """
        Args:
            *arg_blocks: Group to add to report
            blocks: Allows providing the report blocks as a single list
            name: A unique id for the blocks to aid querying (optional)
            label: A label used when displaying the block (optional)
            columns: Display the contained blocks, e.g. Plots, using _n_ columns (default = 1), setting to 0 auto-wraps the columns

        ..tip:: Group can be passed using either arg parameters or the `blocks` kwarg, e.g.
          `dp.Group(plot, table, columns=2)` or `dp.Group(blocks=[plot, table], columns=2)`
        """

        # columns = columns or len(self.blocks)
        self.columns = columns
        super().__init__(*arg_blocks, blocks=blocks, name=name, label=label, columns=columns)


class Toggle(ContainerBlock):
    """
    Toggles act as a container that holds a list of nested Block objects, whose visbility can be toggled on or off by the report viewer
    """

    _tag = "Toggle"

    def __init__(
        self,
        *arg_blocks: BlockOrPrimitive,
        blocks: t.List[BlockOrPrimitive] = None,
        name: BlockId = None,
        label: str = None,
    ):
        """
        Args:
            *arg_blocks: Group to add to report
            blocks: Allows providing the report blocks as a single list
            name: A unique id for the blocks to aid querying (optional)
            label: A label used when displaying the block (optional)
        """
        super().__init__(*arg_blocks, blocks=blocks, name=name, label=label)
        self._wrap_blocks()

    def _wrap_blocks(self) -> None:
        """Wrap the list of blocks in a top-level block element if needed"""
        if len(self.blocks) > 1:
            # only wrap if not all blocks are a Group object
            self.blocks = [Group(blocks=self.blocks)]


class BlockListIterator:
    """Wrapper around default list iterator that supports depth-first traversal of blocks"""

    def __init__(self, _iter):
        # linearise all blocks into a deque as we traverse
        self.nested = deque(_iter)

    def __next__(self) -> Block:
        try:
            b: Block = self.nested.popleft()
        except IndexError:
            raise StopIteration()

        if isinstance(b, ContainerBlock):
            # add the nested iter contents for next "next" call, hence traversing the tree
            self.nested.extendleft(reversed(b.blocks))
        return b

    def __iter__(self):
        return self
