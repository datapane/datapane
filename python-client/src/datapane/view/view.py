from __future__ import annotations

import typing as t

from lxml import etree

from datapane.blocks import Group
from datapane.blocks.base import BlockOrPrimitive
from datapane.blocks.layout import ContainerBlock

if t.TYPE_CHECKING:
    from typing_extensions import Self


class View(ContainerBlock):
    """Top-level object that holds a collection of blocks"""

    _tag = "View"
    fragment: bool = False

    def __init__(self, *arg_blocks: BlockOrPrimitive, blocks: t.List[BlockOrPrimitive] = None, **kwargs):
        # if passed a single View into a View object, pull out the contained blocks and use instead
        if len(arg_blocks) == 1 and isinstance(arg_blocks[0], View):
            arg_blocks = tuple(arg_blocks[0].blocks)

        super().__init__(*arg_blocks, blocks=blocks, **kwargs)

    def __or__(self, other: View) -> View:
        x = Group(blocks=self.blocks) if len(self.blocks) > 1 else self.blocks[0]
        y = Group(blocks=other.blocks) if len(other.blocks) > 1 else other.blocks[0]
        z = Group(x, y, columns=2)
        return View(z)

    @classmethod
    def from_notebook(
        cls, opt_out: bool = True, show_code: bool = False, show_markdown: bool = True, template: str = "auto"
    ) -> Self:
        from datapane.ipython import templates as ip_t
        from datapane.ipython.utils import cells_to_blocks

        blocks = cells_to_blocks(opt_out=opt_out, show_code=show_code, show_markdown=show_markdown)
        app_template_cls = ip_t._registry.get(template) or ip_t.guess_template(blocks)
        app_template = app_template_cls(blocks)
        app_template.transform()
        app_template.validate()
        return cls(blocks=app_template.blocks)

    def get_dom(self) -> str:
        """Return the Document structure for the View"""
        # internal debugging method
        from datapane.processors.file_store import DummyFileEntry, FileStore

        from .xml_visitor import XMLBuilder

        builder = XMLBuilder(FileStore(DummyFileEntry))
        v = self.accept(builder)
        return etree.tounicode(v.elements[0], pretty_print=True)

    def pprint(self) -> None:
        from .visitors import PrettyPrinter

        self.accept(PrettyPrinter())
