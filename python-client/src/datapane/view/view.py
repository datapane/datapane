from __future__ import annotations

import typing as t

pass

from lxml import etree

pass

from datapane.blocks import Group
from datapane.blocks.base import BlockOrPrimitive

pass
from datapane.client import DPClientError
from datapane.client.ipython_utils import cells_to_blocks

pass


if t.TYPE_CHECKING:
    pass
    from typing_extensions import Self

    pass


from datapane.blocks.layout import ContainerBlock


class View(ContainerBlock):
    """Top-level object that holds a collection of blocks"""

    _tag = "View"
    fragment: bool = False

    def __init__(self, *arg_blocks: BlockOrPrimitive, blocks: t.List[BlockOrPrimitive] = None, **kwargs):
        # if passed a single View into a View object, pull out the contained blocks and use instead
        if len(arg_blocks) == 1 and isinstance(arg_blocks[0], View):
            arg_blocks = tuple(arg_blocks[0].blocks)

        super().__init__(*arg_blocks, blocks=blocks, **kwargs)

        if any(isinstance(b, View) for b in self.blocks):
            raise DPClientError("Can't currently nest views")

    # def __init__(
    #     self,
    #     *arg_blocks: BlockOrPrimitive,
    #     blocks: t.List[BlockOrPrimitive] = None,
    # ):
    #     blocks = blocks or list(arg_blocks)
    #     if len(blocks) == 0:
    #         raise DPClientError("Can't create View with 0 objects")
    #     self.blocks = [wrap_block(b) for b in blocks]
    #
    # @classmethod
    # def empty(cls) -> View:
    #     return View(blocks=[Empty()])
    #
    # def __iter__(self):
    #     return BlockListIterator(self.blocks.__iter__())
    #
    # def __add__(self, other: View) -> View:
    #     x = self.blocks + other.blocks
    #     return View(blocks=x)
    #
    # def __and__(self, other: View) -> View:
    #     x = self.blocks + other.blocks
    #     return View(blocks=x)

    def __or__(self, other: View) -> View:
        x = Group(blocks=self.blocks) if len(self.blocks) > 1 else self.blocks[0]
        y = Group(blocks=other.blocks) if len(other.blocks) > 1 else other.blocks[0]
        z = Group(x, y, columns=2)
        return View(z)

    @classmethod
    def from_notebook(cls, opt_out: bool = True) -> Self:
        blocks = cells_to_blocks(opt_out=opt_out)

        return cls(blocks=blocks)

    # def _ipython_display_(self):
    #     """Display the block as a side effect within a Jupyter notebook"""
    #     from IPython.display import HTML, display
    #
    #     from datapane.processors.api import stringify_report
    #
    #     html_str = stringify_report(self)
    #     display(HTML(html_str))
    # def accept(self, visitor: ViewVisitor) -> ViewVisitor:
    #     # TODO - replace
    #     dispatch_to: str = visitor.dispatch_to
    #     f: t.Callable[[ViewVisitor], ViewVisitor] = getattr(self, dispatch_to)
    #     return f(visitor)

    # # todo - move these...
    # def as_xml(self, s: XMLBuilder) -> t.Tuple[Element, FileStore]:
    #     # kick-off the recursive pass of the node-tree
    #     _s = reduce(lambda _s, block: block.accept(_s), self.blocks, s)
    #
    #     # create top-level structure
    #     view_doc: Element = E.View(
    #         # E.Internal(),
    #         *_s.elements,
    #         **mk_attribs(version="1", fragment=self.fragment),
    #     )
    #
    #     return view_doc, _s.store
    #
    # def print(self, s: PrettyPrinter) -> None:
    #     # kick-off the recursive pass of the node-tree
    #     _ = reduce(lambda _s, block: block.accept(_s), self.blocks, s)
    #
    # def run_dynamic(self, s: ApplyDynamic) -> None:
    #     # kick-off the recursive pass of the node-tree
    #     _ = reduce(lambda _s, block: block.accept(_s), self.blocks, s)
    #
    # def collect_interactive(self, s: CollectInteractive) -> None:
    #     # kick-off the recursive pass of the node-tree
    #     _ = reduce(lambda _s, block: block.accept(_s), self.blocks, s)

    def _as_xml_str(self) -> str:
        # internal debugging method
        from datapane.processors.file_store import B64FileEntry, FileStore

        from .xml_visitor import XMLBuilder

        v: XMLBuilder = self.accept(XMLBuilder(FileStore(B64FileEntry)))
        return etree.tounicode(v.elements[0], pretty_print=True)
