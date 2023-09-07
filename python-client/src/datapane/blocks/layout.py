from __future__ import annotations

import typing as t
from collections import deque
from functools import reduce

from datapane.client import DPClientError, log
from datapane.common.dp_types import StrEnum

from .base import BaseBlock, BlockId, BlockList, BlockOrPrimitive, wrap_block
from .empty import Empty, gen_name

if t.TYPE_CHECKING:
    from typing_extensions import Self

    from datapane.blocks import Block

    from .base import VV


class SelectType(StrEnum):
    DROPDOWN = "dropdown"
    TABS = "tabs"


class VAlign(StrEnum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class ContainerBlock(BaseBlock):
    """
    Abstract Block that supports nested/contained blocks
     - represents a subtree in the document
    """

    blocks: BlockList
    # how many blocks must there be in the container
    report_minimum_blocks: int = 1

    def __init__(self, *arg_blocks: BlockOrPrimitive, blocks: t.List[BlockOrPrimitive] = None, **kwargs):
        self.blocks = blocks or list(arg_blocks)
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
    Apps on Datapane can have multiple pages, which are presented to users as tabs at the top of your app. These can be used similarly to sheets in an Excel document.

    To add a page, use the `dp.Page` block at the top-level of your app, and give it a title with the `title` parameter.

    !!! info
        Pages cannot be nested, and can only exist at the root level of your `dp.App` object. If you're using pages, all other blocks must be contained inside a Page block.

    !!! note
        This is included for backwards-compatability, and can be replaced by using Selects going forwards.
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

        !!! tip
            Page can be passed using either arg parameters or the `blocks` kwarg, e.g. `dp.Page(group, select)` or `dp.Group(blocks=[group, select])`
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

    !!! note
        Select expects a list of Blocks, e.g. a Plot or Table, but also includes Select or Groups themselves, but if a Python object is passed, e.g. a Dataframe, Datapane will attempt to convert it automatically.

    """

    _tag = "Select"
    report_minimum_blocks = 2

    def __init__(
        self,
        *arg_blocks: BlockOrPrimitive,
        blocks: t.List[BlockOrPrimitive] = None,
        type: SelectType = SelectType.TABS,
        name: BlockId = None,
        label: str = None,
    ):
        """
        Args:
            *arg_blocks: Page to add to report
            blocks: Allows providing the report blocks as a single list
            type: An instance of SelectType that indicates if the select should use tabs or a dropdown (default: Tabs)
            name: A unique id for the blocks to aid querying (optional)
            label: A label used when displaying the block (optional)

        !!! tip
            Select can be passed using either arg parameters or the `blocks` kwarg, e.g. `dp.Select(table, plot, type=dp.SelectType.TABS)` or `dp.Select(blocks=[table, plot])`
        """
        super().__init__(*arg_blocks, blocks=blocks, name=name, label=label, type=type)
        if len(self.blocks) < 2:
            log.info("Creating a Select with less than 2 objects")


class Group(ContainerBlock):
    """
    If you pass a list of blocks (such as `Plot` and `Table`) to an app, they are -- by default -- laid out in a single column with a row per block.

    If you would like to customize the rows and columns, Datapane provides a `Group` block which takes a list of blocks and a number of columns and lays them out in a grid.

    !!! tip
        As `Group` blocks are blocks themselves, they are composable, and you can create more custom layers of nested blocks, for instance nesting 2 rows in the left column of a 2 column layout
    """

    _tag = "Group"

    def __init__(
        self,
        *arg_blocks: BlockOrPrimitive,
        blocks: t.List[BlockOrPrimitive] = None,
        name: BlockId = None,
        label: t.Optional[str] = None,
        widths: t.Optional[t.List[t.Union[int, float]]] = None,
        valign: VAlign = VAlign.TOP,
        columns: int = 1,
    ):
        """
        Args:
            *arg_blocks: Group to add to report
            blocks: Allows providing the report blocks as a single list
            name: A unique id for the blocks to aid querying (optional)
            label: A label used when displaying the block (optional)
            widths: A list of numbers representing the proportion of vertical space given to each column (optional)
            valign: The vertical alignment of blocks in the Group (default = VAlign.TOP)
            columns: Display the contained blocks, e.g. Plots, using _n_ columns (default = 1), setting to 0 auto-wraps the columns

        !!! note
            Group can be passed using either arg parameters or the `blocks` kwarg, e.g. `dp.Group(plot, table, columns=2)` or `dp.Group(blocks=[plot, table], columns=2)`.
        """

        if widths is not None and len(widths) != columns:
            raise DPClientError("Group 'widths' list length does not match number of columns")

        # columns = columns or len(self.blocks)
        self.columns = columns
        super().__init__(
            *arg_blocks, blocks=blocks, name=name, label=label, columns=columns, widths=widths, valign=valign
        )


class Toggle(ContainerBlock):
    """
    Toggles act as a container that holds a list of nested Block objects, whose visibility can be toggled on or off by the report viewer
    """

    _tag = "Toggle"
    report_minimum_blocks = 1

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
