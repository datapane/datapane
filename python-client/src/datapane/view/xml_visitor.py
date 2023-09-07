# flake8: noqa:F811
from __future__ import annotations

import dataclasses as dc
import typing as t
from collections import namedtuple

from lxml import etree
from lxml.builder import ElementMaker
from multimethod import DispatchError, multimethod

from datapane import DPClientError
from datapane.blocks import BaseBlock
from datapane.blocks.asset import AssetBlock
from datapane.blocks.empty import gen_name
from datapane.blocks.layout import ContainerBlock
from datapane.blocks.text import EmbeddedTextBlock
from datapane.client import log
from datapane.common.viewxml_utils import ElementT, mk_attribs
from datapane.view.view_blocks import Blocks
from datapane.view.visitors import ViewVisitor

if t.TYPE_CHECKING:
    from datapane.processors import FileEntry, FileStore

    # from typing_extensions import Self

E = ElementMaker()  # XML Tag Factory


@dc.dataclass
class XMLBuilder(ViewVisitor):
    """Convert the Blocks into an XML document"""

    store: FileStore
    # element: t.Optional[etree.Element] = None  # Empty Group Element?
    elements: t.List[ElementT] = dc.field(default_factory=list)

    def get_root(self, fragment: bool = False) -> ElementT:
        """Return the top-level ViewXML"""
        # create the top-level

        # get the top-level root
        _top_group: ElementT = self.elements.pop()
        assert _top_group.tag == "Group"
        assert not self.elements

        # create top-level structure
        return E.View(
            # E.Internal(),
            *_top_group.getchildren(),
            **mk_attribs(version="1", fragment=fragment),
        )

    @property
    def store_count(self) -> int:
        return len(self.store.files)

    def add_element(self, _: BaseBlock, e: etree.Element) -> XMLBuilder:
        """Add an element to the list of nodes at the current XML tree location"""
        self.elements.append(e)
        return self

    # xml convertors
    @multimethod
    def visit(self, b: BaseBlock) -> XMLBuilder:
        """Base implementation - just created an empty tag including all the initial attributes"""
        _E = getattr(E, b._tag)
        return self.add_element(b, _E(**b._attributes))

    def _visit_subnodes(self, b: ContainerBlock) -> t.List[ElementT]:
        cur_elements = self.elements
        self.elements = []
        b.traverse(self)  # visit subnodes
        res = self.elements
        self.elements = cur_elements
        return res

    @multimethod
    def visit(self, b: ContainerBlock) -> XMLBuilder:
        sub_elements = self._visit_subnodes(b)
        # build the element
        _E = getattr(E, b._tag)
        element = _E(*sub_elements, **b._attributes)
        return self.add_element(b, element)

    @multimethod
    def visit(self, b: Blocks) -> XMLBuilder:
        sub_elements = self._visit_subnodes(b)

        # Blocks are converted to Group internally
        if label := b._attributes.get("label"):
            log.info(f"Found label {label} in top-level Blocks/View")
        element = E.Group(*sub_elements, columns="1", valign="top")
        return self.add_element(b, element)

    @multimethod
    def visit(self, b: EmbeddedTextBlock) -> XMLBuilder:
        # NOTE - do we use etree.CDATA wrapper?
        _E = getattr(E, b._tag)
        return self.add_element(b, _E(etree.CDATA(b.content), **b._attributes))

    @multimethod
    def visit(self, b: AssetBlock):
        """Main XMl creation method - visitor method"""
        fe = self._add_asset_to_store(b)

        _E = getattr(E, b._tag)

        e: etree._Element = _E(
            type=fe.mime,
            # size=conv_attrib(fe.size),
            # hash=fe.hash,
            **{**b._attributes, **b.get_file_attribs()},
            # src=f"attachment://{self.store_count}",
            src=f"ref://{fe.hash}",
        )

        if b.caption:
            e.set("caption", b.caption)
        return self.add_element(b, e)

    def _add_asset_to_store(self, b: AssetBlock) -> FileEntry:
        """Default asset store handler that operates on native Python objects"""
        # import here as a very slow module due to nested imports
        # from .. import files

        # check if we already have stored this asset to the store
        # TODO - do we just persist the asset store across the session??
        if b._prev_entry:
            if type(b._prev_entry) == self.store.fw_klass:
                self.store.add_file(b._prev_entry)
                return b._prev_entry
            else:
                b._prev_entry = None

        if b.data is not None:
            # fe = files.add_to_store(self.data, s.store)
            try:
                writer = get_writer(b)
                meta: AssetMeta = writer.get_meta(b.data)
                fe = self.store.get_file(meta.ext, meta.mime)
                writer.write_file(b.data, fe.file)
                self.store.add_file(fe)
            except DispatchError:
                raise DPClientError(f"{type(b.data).__name__} not supported for {self.__class__.__name__}")
        elif b.file is not None:
            fe = self.store.load_file(b.file)
        else:
            raise DPClientError("No asset to add")

        b._prev_entry = fe
        return fe


AssetMeta = namedtuple("AssetMeta", "ext mime")


class AssetWriterP(t.Protocol):
    """Implement these in any class to support asset writing
    for a particular AssetBlock"""

    def get_meta(self, x: t.Any) -> AssetMeta:
        ...

    def write_file(self, x: t.Any, f) -> None:
        ...


asset_mapping: t.Dict[t.Type[AssetBlock], t.Type[AssetWriterP]] = dict()


def get_writer(b: AssetBlock) -> AssetWriterP:
    import datapane.blocks.asset as a

    from . import asset_writers as aw

    if not asset_mapping:
        asset_mapping.update(
            {
                a.Plot: aw.PlotWriter,
                a.Table: aw.HTMLTableWriter,
                a.DataTable: aw.DataTableWriter,
                a.Attachment: aw.AttachmentWriter,
            }
        )
    return asset_mapping[type(b)]()
