from __future__ import annotations

import re
import typing as t
from collections import deque
from pathlib import Path

from dominate.dom_tag import dom_tag

from datapane.client import DPClientError
from datapane.common import NPath, utf_read_text
from datapane.common.viewxml_utils import get_embed_url

from .base import BlockId, BlockOrPrimitive, DataBlock, wrap_block
from .layout import Group


class EmbeddedTextBlock(DataBlock):
    """
    Abstract Block for embedded text formats that are stored directly in the
    document (rather than external references)
    """

    content: str

    def __init__(self, content: str, name: BlockId = None, **kwargs):
        super().__init__(name, **kwargs)
        self.content = content.strip()


class Text(EmbeddedTextBlock):
    """
    Markdown objects store Markdown text that can be displayed as formatted text when viewing your report.

    ..note:: This object is also available as `dp.Text`, and any strings provided directly to the Report/Group object are converted automatically to Markdown blocks

    ..tip:: You can also insert a dataframe in a Markdown block as a table by using `df.to_markdown()`, or use dp.Table or dp.DataTable for dedicated dataframe tables.
    """

    _tag = "Text"

    def __init__(self, text: str = None, file: NPath = None, name: BlockId = None, label: str = None):
        """
        Args:
            text: The markdown formatted text, use triple-quotes, (`\"\"\"# My Title\"\"\"`) to create multi-line markdown text
            file: Path to a file containing markdown text
            name: A unique name for the block to reference when adding text or embedding (optional)
            label: A label used when displaying the block (optional)

        ..note:: File encodings are auto-detected, if this fails please read the file manually with an explicit encoding and use the text parameter on dp.Attachment
        """
        if text:
            text = text.strip()

        assert text or file
        content = text or utf_read_text(Path(file).expanduser())
        super().__init__(content=content, name=name, label=label)

    def format(self, *args: BlockOrPrimitive, **kwargs: BlockOrPrimitive) -> Group:
        """
        Format the markdown text template, using the supplied context to insert blocks into `{{}}` markers in the template.

        `{}` markers can be empty, hence positional, or have a name, e.g. `{{plot}}`, which is used to lookup the value from the keyword context.

        Args:
            *args: positional template context arguments
            **kwargs: keyword template context arguments

        ..tip:: Either Python objects, e.g. dataframes, and plots, or Datapane blocks as context

        Returns:
            A datapane Group object containing the list of text and embedded objects
        """

        splits = re.split(r"\{\{(\w*)\}\}", self.content)
        deque_args = deque(args)
        blocks = []

        for (i, x) in enumerate(splits):
            is_block = bool(i % 2)

            if is_block:
                try:
                    if x:
                        blocks.append(wrap_block(kwargs[x]))
                    else:
                        blocks.append(wrap_block(deque_args.popleft()))
                except (IndexError, KeyError):
                    raise DPClientError(f"Unknown/missing object '{x}' referenced in Markdown format")

            else:
                x = x.strip()
                if x:
                    blocks.append(Text(x))

        return Group(blocks=blocks)


class Divider(EmbeddedTextBlock):
    """
    Divider blocks add a horizontal line to your report, normally used to break up report contents
    # TODO - turn into a component function, doesn't need to be a block type
    """

    _tag = "Text"

    def __init__(self):
        # `---` is processed as a horizontal divider by the FE markdown renderer
        super().__init__(content="---")


class Code(EmbeddedTextBlock):
    """
    Code objects store source code that can be displayed as formatted text when viewing your report.
    """

    _tag = "Code"

    def __init__(
        self, code: str, language: str = "python", caption: str = None, name: BlockId = None, label: str = None
    ):
        """
        Args:
            code: The source code
            language: The language of the code, most common languages are supported (optional - defaults to Python)
            caption: A caption to display below the Code (optional)
            name: A unique name for the block to reference when adding text or embedding (optional)
            label: A label used when displaying the block (optional)
        """
        super().__init__(content=code, language=language, caption=caption, name=name, label=label)


class HTML(EmbeddedTextBlock):
    """
    HTML blocks can be used to embed an arbitrary HTML fragment in a report.
    """

    _tag = "HTML"

    def __init__(self, html: t.Union[str, dom_tag], name: BlockId = None, label: str = None):
        """
        Args:
            html: The HTML fragment to embed - can be a string or a [dominate](https://github.com/Knio/dominate/) tag
            name: A unique name for the block to reference when adding text or embedding (optional)
            label: A label used when displaying the block (optional)
        """
        super().__init__(content=str(html), name=name, label=label)


class Formula(EmbeddedTextBlock):
    """
    Formula blocks can be used to embed LaTeX in a report.
    """

    _tag = "Formula"

    def __init__(self, formula: str, caption: str = None, name: BlockId = None, label: str = None):
        r"""
        Args:
            formula: The formula to embed, using LaTeX format (use raw strings)
            caption: A caption to display below the Formula (optional)
            name: A unique name for the block to reference when adding text or embedding (optional)
            label: A label used when displaying the block (optional)

            ..note:: LaTeX commonly uses special characters, hence prefix your formulas with `r` to make them
            raw strings, e.g. r"\frac{1}{\sqrt{x^2 + 1}}"
        """
        super().__init__(content=formula, caption=caption, name=name, label=label)


class Embed(EmbeddedTextBlock):
    """
    Embed blocks allow HTML from OEmbed providers (e.g. Youtube, Twitter, Vimeo) to be embedded in a report.
    """

    _tag = "Embed"

    def __init__(self, url: str, width: int = 960, height: int = 540, name: BlockId = None, label: str = None):
        """
        Args:
            url: The URL of the resource to be embedded
            width: The width of the embedded object (optional)
            height: The height of the embedded object (optional)
            name: A unique name for the block to reference when adding text or embedding (optional)
            label: A label used when displaying the block (optional)
        """

        result = get_embed_url(url, width=width, height=height)

        # if "html" not in result:
        #     raise DPError(f"Can't embed result from provider for URL '{url}'")
        super().__init__(
            content=result.html, name=name, label=label, url=url, title=result.title, provider_name=result.provider
        )
