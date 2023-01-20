"""
Conversion templates for IPython notebooks to Datapane apps.

..note: Early stage feature - a diverse set of templates that are subject to change.
  Most implementations are currently low-level and will be replaced with higher-level abstractions over time.
"""
from __future__ import annotations

import typing as t
from abc import abstractmethod

import datapane.client.api.report.blocks as b
from datapane.client.exceptions import BlocksNotFoundException
from datapane.client.utils import display_msg

BlockFilterF = t.Callable[[b.BaseElement], bool]
BlockTypes = t.Union[t.Tuple[t.Type[b.BaseElement], ...], t.Type]
BaseElementList = t.List[b.BaseElement]

_registry: t.Dict[str, t.Type[IPythonTemplate]] = {}


def partition_blocks_by_predicates(
    blocks: BaseElementList, predicates: t.List[BlockFilterF]
) -> t.List[BaseElementList]:
    """Partition blocks by predicates"""
    partitions: t.List[BaseElementList] = [[] for _ in range(len(predicates))]

    for block in blocks:
        for i, pred in enumerate(predicates):
            if pred(block):
                partitions[i].append(block)
                break

    return partitions


def partition_blocks_by_types(
    blocks: BaseElementList, partition_types: t.List[t.Type[b.BaseElement]]
) -> t.List[BaseElementList]:
    """Partition blocks by types"""

    predicates: t.List[BlockFilterF] = [
        lambda block, partition_type=partition_type: isinstance(block, partition_type)  # type: ignore # https://github.com/python/mypy/issues/12557, https://github.com/python/mypy/issues/4226
        for partition_type in partition_types
    ]
    partitions: t.List[BaseElementList] = partition_blocks_by_predicates(blocks, predicates)

    return partitions


def filter_blocks_by_predicate(blocks: BaseElementList, predicate: BlockFilterF) -> BaseElementList:
    """Filter blocks by predicates"""
    filtered_blocks, *_ = partition_blocks_by_predicates(blocks, [predicate])

    return filtered_blocks


def filter_blocks_by_types(blocks: BaseElementList, block_types: BlockTypes) -> BaseElementList:
    """Filter blocks by type"""
    filtered_blocks, *_ = partition_blocks_by_predicates(blocks, [lambda block: isinstance(block, block_types)])

    return filtered_blocks


def guess_template(blocks: BaseElementList) -> t.Type[IPythonTemplate]:
    """Guess the template to use based on the blocks provided"""
    app_template: t.Type[IPythonTemplate]

    # DashboardTemplate: Contains only Plot, BigNumber, and DataTable blocks
    if all([isinstance(block, (b.Plot, b.BigNumber, b.DataTable)) for block in blocks]):
        app_template = DashboardTemplate
    # TitledPagesTemplate: Contains text blocks with at least two headings
    elif (
        len(
            filter_blocks_by_predicate(
                blocks, lambda block: isinstance(block, b.Text) and block.content.startswith("# ")
            )
        )
        >= 2
    ):
        app_template = TitledPagesTemplate
    # DescriptivePagesTemplate: Contains at least two text blocks that are followed by a different block type
    elif "".join(["1" if isinstance(block, (b.Text)) else "0" for block in blocks]).count("10") >= 2:
        app_template = DescriptivePagesTemplate
    # AssetListTemplate: Does not contain any text or code blocks
    elif not any(filter_blocks_by_types(blocks, (b.Text, b.Code))):
        app_template = AssetListTemplate
    # AssetCodeListTemplate: Does not contain any text blocks
    elif not any(filter_blocks_by_types(blocks, b.Text)):
        app_template = AssetCodeListTemplate
    # ReportTemplate: The default template if we can't make a guess
    else:
        app_template = ReportTemplate

    display_msg(
        f"Automatically selecting the `{app_template.name}` template. You can override this with `template=template_name` from the following templates: {', '.join(_registry.keys())}."
    )

    return app_template


class IPythonTemplate:
    name: str = "IPythonTemplate"

    def __init__(self, blocks):
        self.blocks = blocks

    @classmethod
    def __init_subclass__(cls, template_name, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.name = template_name
        _registry[template_name] = cls

    @abstractmethod
    def transform(self) -> None:
        raise NotImplementedError

    def validate(self):
        if not self.blocks:
            raise BlocksNotFoundException("No blocks required by template were found.")


class ReportTemplate(IPythonTemplate, template_name="report"):
    """Creates a report with blocks in the given order"""

    def transform(self) -> None:
        pass


class DashboardTemplate(IPythonTemplate, template_name="dashboard"):
    """Creates a dashboard with a 3 column group of BigNumbers, followed by a 2 column group of Plots"""

    def transform(self) -> None:
        blocks: BaseElementList = self.blocks

        big_numbers, plots, tables = partition_blocks_by_types(
            blocks,
            [b.BigNumber, b.Plot, b.DataTable],
        )

        blocks = []

        if big_numbers:
            blocks.append(b.Group(blocks=big_numbers, columns=3))

        tabs: BaseElementList = []

        if plots:
            tabs.append(b.Group(blocks=plots, columns=2, label="Figures"))

        if tables:
            tabs.append(b.Group(blocks=tables, label="Tables"))

        # We may only have plots or tables, so we don't need to use a Select block
        if tabs:
            if len(tabs) > 1:
                blocks.append(b.Select(blocks=tabs))
            else:
                blocks.append(tabs[0])

        self.blocks = blocks


class AssetListTemplate(IPythonTemplate, template_name="asset_list"):
    """Starts a new page for every supported Datapane block"""

    def transform(self) -> None:
        blocks = filter_blocks_by_predicate(self.blocks, lambda block: not isinstance(block, (b.Code, b.Text)))
        pages: t.List[b.LayoutBlock] = [
            b.Page(blocks=[block], title=f"{idx + 1}. {block._tag}") for idx, block in enumerate(blocks)
        ]
        self.blocks = pages


class AssetCodeListTemplate(IPythonTemplate, template_name="asset_code_list"):
    """Starts a new page for every supported Datapane block, with the code block after the asset"""

    def transform(self) -> None:
        blocks = self.blocks
        pages: t.List[b.LayoutBlock] = []
        last_block: t.Optional[b.BaseElement] = None

        for block in blocks:
            # If the block is not a Code or Text block, add it to a new page
            if not isinstance(block, (b.Text, b.Code)):
                # If the last block was a code block, add it to the current page
                if isinstance(last_block, b.Code):
                    pages.append(
                        b.Page(
                            blocks=[b.Group(block, last_block)],
                            title=f"{len(pages) + 1}. {block._tag}",
                        )
                    )
                else:
                    pages.append(b.Page(blocks=[block], title=f"{len(pages) + 1}. {block._tag}"))

            last_block = block
        self.blocks = pages


class DescriptivePagesTemplate(IPythonTemplate, template_name="descriptive_pages"):
    """Start a new page every time a contiguous block of text is encountered"""

    def transform(self) -> None:
        blocks = self.blocks
        pages: t.List[b.LayoutBlock] = []
        page_blocks: BaseElementList = []
        last_block: t.Optional[b.BaseElement] = None
        page_title: str = "Page 1"

        for block in blocks:
            # If the block is a Text block, and the last block was not a Text block, start a new page
            if isinstance(block, b.Text) and not isinstance(last_block, b.Text):
                if page_blocks:
                    pages.append(b.Page(blocks=page_blocks, title=page_title))
                    page_blocks = []

                if block.content.startswith("# "):
                    page_title = block.content.partition("\n")[0].lstrip("# ").strip()
                else:
                    page_title = f"Page {len(pages) + 1}"

            page_blocks.append(block)
            last_block = block

        # add the last page
        pages.append(b.Page(blocks=page_blocks, title=page_title))
        self.blocks = pages


class TitledPagesTemplate(IPythonTemplate, template_name="titled_pages"):
    """Start a new page every time heading (#) text is encountered"""

    def transform(self) -> None:
        blocks = self.blocks
        pages: t.List[b.LayoutBlock] = []
        page_blocks: BaseElementList = []
        page_title: str = "Page 1"

        for block in blocks:
            # If the block is a Text block, and it starts with a # heading, start a new page
            if isinstance(block, b.Text):
                if block.content.startswith("# "):
                    if page_blocks:
                        pages.append(b.Page(blocks=page_blocks, title=page_title))
                        page_blocks = []

                    page_title = block.content.partition("\n")[0].lstrip("#").strip()

            page_blocks.append(block)

        # add the last page
        pages.append(b.Page(blocks=page_blocks, title=page_title))
        self.blocks = pages
