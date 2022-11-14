# flake8: noqa:F811
from __future__ import annotations

import abc
import dataclasses as dc
import typing
import typing as t

pass

from multimethod import multimethod

from datapane.blocks import BaseElement, Interactive
from datapane.blocks.layout import ContainerBlock

TV = typing.TypeVar("TV", bound="ViewVisitor")

if t.TYPE_CHECKING:
    from datapane.app.runtime import FEntries

    pass


@dc.dataclass
class ViewVisitor(abc.ABC):
    dispatch_to: t.ClassVar[str]

    @multimethod
    def visit(self: TV, b: BaseElement) -> TV:
        return self


@dc.dataclass
class PrettyPrinter(ViewVisitor):
    """Print out the view in an indented, XML-like tree form"""

    indent: int = 1
    # dispatch_to = "print"

    @multimethod
    def visit(self, b: BaseElement):
        print("|", "-" * self.indent, str(b), sep="")

    @multimethod
    def visit(self, b: ContainerBlock):
        print("|", "-" * self.indent, str(b), sep="")
        self.indent += 2
        _ = b.traverse(self)
        self.indent -= 2


# # TODO - combine into a general Interactive Pass here?
# @dc.dataclass
# class ApplyDynamic(ViewVisitor):
#     """Print out the view in an indented, XML-like tree form"""
#
#     indent: int = 1
#     dispatch_to = "dynamic"
#
#     @multimethod
#     def visit(self, b: BaseElement):
#         pass
#
#     @multimethod
#     def visit(self, b: ContainerBlock):
#         reduce(lambda _s, block: block.accept(_s), b.blocks, self)
#
#     @multimethod
#     def visit(self, b: Dynamic):
#         # run the function, then recurse inside
#         view: View = b.function()
#         reduce(lambda _s, block: block.accept(_s), view.blocks, self)


@dc.dataclass
class CollectInteractive(ViewVisitor):
    """Print out the view in an indented, XML-like tree form"""

    entries: FEntries = dc.field(default_factory=dict)
    dispatch_to = "collect_interactive"

    @multimethod
    def visit(self, b: BaseElement):
        return self

    @multimethod
    def visit(self, b: ContainerBlock):
        b.traverse(self)

    @multimethod
    def visit(self, b: Interactive):
        # TODO - move this to common.types??
        from datapane.app.runtime import InteractiveRef

        # NOTE - do we move to a method on Interactive??
        self.entries[b.function_id] = InteractiveRef(
            f=b.function, f_id=b.function_id, controls=b.controls, cache=b.cache, swap=b.swap
        )
