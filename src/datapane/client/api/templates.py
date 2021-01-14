"""
Datapane helper functions to make creating your reports a bit simpler and reduce common tasks

..note:: Please submit any new templates you've used to our repo - it's open-source and will help everyone in creating great reports!
"""
import random
import typing as t
from copy import deepcopy
from pathlib import Path

import importlib_resources as ir
import numpy as np
import pandas as pd

from datapane.common import NPath

from .report import blocks as b
from .report.core import Report

__all__ = ["add_code", "add_header", "add_footer", "build_md_report", "build_demo_report"]


def _map_page_blocks(page: b.Page, f: t.Callable[[b.BlockList], b.BlockList]) -> b.Page:
    page.blocks = f(page.blocks)
    return page


def _map_report_pages(r: Report, f: t.Callable[[b.Page], b.Page], all_pages: bool = True) -> Report:
    def g(i: int, page: b.Page) -> b.Page:
        return f(page) if all_pages or i == 0 else page

    r.pages = [g(*x) for x in enumerate(r.pages)]
    return r


def add_code(block: b.BlockOrPrimitive, code: str, language: str = "python") -> b.Select:
    """
    Attach code fragment to an existing plot/figure/dataframe for use within a report

    Args:
        block: The existing object to add code to - can be either an existing dp Block or an Python object
        code: The code fragment to add
        language: The language of the code fragment (optional)

    Returns:
        A Select block that provides the figure and the code in tabs that can be selected by the user
    """

    w_block = b.wrap_block(block)
    w_block._add_attributes(label="Figure")
    return b.Select(w_block, b.Code(code, language, label="Code"), type=b.SelectType.TABS)


def build_md_report(
    text_or_file: t.Union[str, NPath],
    *args: b.BlockOrPrimitive,
    **kwargs: b.BlockOrPrimitive,
) -> Report:
    """
    An easy way to build a complete report from a single top-level markdown text / file template.
    Any additional context can be passed in and will be inserted into the Markdown template.

    Args:
        text_or_file: The markdown text, or path to a markdown file, using {} for templating
        *args: positional template context arguments
        **kwargs: keyword template context arguments

    Returns:
        A datapane Report object for saving or publishing

    ..tip:: either text or file is required
    ..tip:: Either Python objects, e.g. dataframes, and plots, or Datapane blocks as context

    """
    try:
        b_text = b.Text(file=text_or_file) if Path(text_or_file).exists() else b.Text(text=text_or_file)
    except OSError:
        b_text = b.Text(text=text_or_file)

    group = b_text.format(*args, **kwargs)
    return Report(b.Page(group))


def add_header(report: Report, header: b.BlockOrPrimitive, all_pages: bool = True) -> Report:
    """
    Add a header to the report, returning a modified version of the same report

    Args:
        report: The report to add the header to
        header: The header block - this can be any dp Block, e.g a File, Plot, Logo, or anything
        all_pages: Apply the header to all pages or just the first page only

    Returns:
        A modified report with the header applied
    """

    report = deepcopy(report)
    return _map_report_pages(
        report, lambda p: _map_page_blocks(p, lambda blocks: [b.Group(blocks=[header] + p.blocks)]), all_pages=all_pages
    )


def add_footer(report: Report, footer: b.BlockOrPrimitive, all_pages: bool = True) -> Report:
    """
    Add a footer to the report, returning a modified version of the same report

    Args:
        report: The report to add the header to
        footer: The footer block - this can be any dp Block, e.g a File, Plot, Logo, or anything
        all_pages: Apply the header to all pages or just the first page only

    Returns:
        A modified report with the footer applied
    """
    report = deepcopy(report)
    return _map_report_pages(
        report, lambda p: _map_page_blocks(p, lambda blocks: [b.Group(blocks=p.blocks + [footer])]), all_pages=all_pages
    )


def build_demo_report() -> Report:
    """
    Generate a sample demo report

    Returns:
        A datapane Report object for saving or publishing

    """

    import altair as alt  # noqa
    import matplotlib.pyplot as plt  # noqa
    import plotly.graph_objects as go  # noqa
    from bokeh.plotting import figure  # noqa
    import folium  # noqa

    def gen_df(dim: int = 4) -> pd.DataFrame:
        axis = [i for i in range(0, dim)]
        data = {"x": axis, "y": axis}
        return pd.DataFrame.from_dict(data)

    def gen_bokeh(**kw):
        p = figure(title="simple line example", x_axis_label="x", y_axis_label="y", **kw)
        p.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], legend_label="Temp.", line_width=2)
        return p

    def gen_plotly():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, 1, 2, 3, 4, 5], y=[1.5, 1, 1.3, 0.7, 0.8, 0.9]))
        fig.add_trace(go.Bar(x=[0, 1, 2, 3, 4, 5], y=[1, 0.5, 0.7, -1.2, 0.3, 0.4]))
        return fig

    def gen_matplotlib():
        # pd.set_option("plotting.backend", "matplotlib")
        fig, ax = plt.subplots()
        df = gen_df()
        ax.plot(df["x"], df["y"])
        # gen_df().plot.scatter("x", "y", ax=ax)
        return fig

    def gen_html(w: int = 30, h: int = 30):
        return b.HTML(
            f"""
    <div style="width: {w}rem; height: {h}rem; background-color: rgba(0, 0, 255, 0.2); position: relative">
        <div style="position: absolute; right: 50%; bottom: 50%; transform: translate(50%, 50%);">
            HTML Block
        </div>
    </div>"""
        )

    def color_large_vals(s):
        return ["background-color: rgba(255, 0, 0, 0.3)" if val > 800 else "" for val in s]

    def gen_table_df(rows: int = 4, alphabet: str = "ABCDEF") -> pd.DataFrame:
        data = [{x: random.randint(0, 1000) for x in alphabet} for _ in range(0, rows)]
        return pd.DataFrame.from_dict(data)

    def gen_folium():
        return folium.Map(location=[45.372, -121.6972], zoom_start=12, tiles="Stamen Terrain")

    df1 = gen_table_df(10)
    styler1 = df1.style.apply(color_large_vals, axis=1).hide_index()

    def _vega_sine():
        x = np.arange(100)
        source = pd.DataFrame({"x": x, "f(x)": np.sin(x / 5)})

        return alt.Chart(source).mark_line().encode(x="x", y="f(x)")

    vega_sine = _vega_sine()

    def _vega_bar():
        source = pd.DataFrame(
            {"a": ["A", "B", "C", "D", "E", "F", "G", "H", "I"], "b": [28, 55, 43, 91, 81, 53, 19, 87, 52]}
        )

        return alt.Chart(source).mark_bar().encode(x="a", y="b")

    vega_bar = _vega_bar()

    basics = """
This page describes Datapane, an API for creating data-driven reports from Python.
Datapane reports are comprised of blocks, which can be collected together and laid-out to form multiple-pages reports.
Some of the basic blocks include tables and plots.

## Tables

The Table block displays a tabular set of data, and takes either a dataframe or a pandas Styler "styled" object,

```python
dp.Table(df, caption="A Table")
```

{{table}}

The DataTable block also takes a dataframe and allows the user to search and filter the data when viewing the report


## Plots

The Plot block supports Altair, Bokeh, Plotly, Matplotlib, and Folium plots,

```python
dp.Plot(altair_plot, caption="A Plot")
```

{{plot}}

## Other Blocks

Datapane has many other block types, including files, embeds, images, and big numbers - see the Blocks page for more info.

Additionally layout blocks provide the ability nest blocks to create groups of columns and user selections - see the Layout page for more info.

{{other}}


    """
    logo = ir.files("datapane.resources.templates") / "datapane-logo.png"
    other = b.Group(
        b.File(file=logo),
        b.BigNumber(heading="Datapane Blocks", value=11, prev_value=6, is_upward_change=True),
        rows=1,
        columns=0,
    )
    page_1 = b.Page(
        b.Text(basics).format(table=b.Table(gen_table_df(), caption="A table"), plot=vega_sine, other=other),
        label="Intro",
    )

    layout = """
Blocks on a page can be laid-out in Datapane using a flexible row and column system. furthermore, multiple blocks can be
nested into a single block where the user can select between which block, e.g. a plot, to view.
See https://docs.datapane.com/reports/layout-and-customization for more info.

## Group Blocks

Group blocks allow you to take a list of blocks, and lay-them out over a number of `rows` and `columns`, allowing you to create 2-column layouts, grids, and more,

```python
dp.Group(plot1, plot2, columns=2)
cells = [dp.Text(f"### Cell {x}") for x in range(6)]
dp.Group(*cells, rows=2, columns=0)  # 0 implies auto
```

{{group1}}

{{group2}}

## Select Blocks

Select blocks allow you to collect a list of blocks, e.g. plots, and allow the user to select between them, either via tabs or a dropdown list.

```python
dp.Select(plot1, plot2, type=dp.SelectType.TABS)
dp.Select(plot1, plot2, type=dp.SelectType.DROPDOWN)
```

{{select1}}

{{select2}}


Both Group and Select blocks can be nested within one another, in any order to create, for instance dropdowns with 2 columns inside, as below

```python
group1 = dp.Group(plot1, plot2, columns=2)
dp.Select(group1, df)
```

{{nested}}
"""

    group1 = b.Group(vega_bar, vega_sine, columns=2)
    group2 = b.Group(*[f"### Cell {x}" for x in range(6)], rows=2, columns=0)
    select1 = b.Select(vega_bar, vega_sine, type=b.SelectType.TABS)
    select2 = b.Select(vega_bar, vega_sine, type=b.SelectType.DROPDOWN)

    nested = b.Select(group1, b.Table(gen_table_df()))
    page_2 = b.Page(
        b.Text(layout).format(group1=group1, group2=group2, select1=select1, select2=select2, nested=nested),
        label="Layout",
    )

    adv_blocks = """
A list and demonstration of all the blocks supported by Datapane - see https://docs.datapane.com/reports/blocks for more info.

## Plot Blocks

```python
dp.Group(dp.Plot(altair_plot, caption="Altair Plot"),
         dp.Plot(bokeh_plot, caption="Bokeh Plot"),
         dp.Plot(matplotlib_plot, caption="Matplotlib Plot"),
         dp.Plot(plotly_plot, caption="Plotly Plot"),
         dp.Plot(folium_plot, caption="Folium Plot"),
         columns=2)
```

{{plots}}

## Table Blocks

```python
dp.Table(df, caption="Basic Table")
dp.Table(styled_df, caption="Styled Table")
dp.DataTable(df, caption="Interactive DataTable")
```

{{tables}}

## Text Blocks

```python
dp.Text("Hello, __world__!")
dp.Code("print('Hello, world!')")
dp.HTML("<h1>Hello World</h1>")
dp.BigNumber(heading="Datapane Blocks", value=11, prev_value=6, is_upward_change=True)
```

{{text}}

## Embedding

You can embed any URLs that spport the OEmbed protocol, including YouTube and Twitter.

```python
dp.Embed("https://www.youtube.com/watch?v=JDe14ulcfLA")
dp.Embed("https://twitter.com/datapaneapp/status/1300831345413890050")
```

{{embed}}

## Files

Files and Python objects can be added to a Datapane report, and be viewed (depending on browser support) and downloaded.

```python
dp.File(file="./logo.png")
dp.File(data=[1,2,3], is_json=True)
dp.File(data=[1,2,3], is_json=False)  # store as a pickle
```

{{files}}

    """

    plots = b.Group(
        b.Plot(vega_sine, caption="Altair Plot"),
        b.Plot(gen_bokeh(), caption="Bokeh Plot"),
        b.Plot(gen_matplotlib(), caption="Matplotlib Plot"),
        b.Plot(gen_plotly(), caption="Plotly Plot"),
        b.Plot(gen_folium(), caption="Folium Plot"),
        columns=2,
    )
    tables = b.Group(
        b.Table(df1, caption="Basic Table"),
        b.Table(styler1, caption="Styled Table"),
        b.DataTable(df1, caption="Interactive DataTable"),
    )
    text = b.Group(
        b.Text("Hello, __world__!"),
        b.Code("print('Hello, world!'"),
        b.HTML("<h1>Hello World</h1>"),
        b.BigNumber(heading="Datapane Blocks", value=11, prev_value=6, is_upward_change=True),
        rows=1,
        columns=0,
    )
    embed = b.Group(
        b.Embed("https://www.youtube.com/watch?v=JDe14ulcfLA"),
        b.Embed("https://twitter.com/datapaneapp/status/1300831345413890050"),
        columns=2,
    )
    files = b.Group(
        b.File(file=logo),
        b.File(data=[1, 2, 3], is_json=True),
        b.File(data=[1, 2, 3], is_json=False),
        rows=1,
        columns=0,
    )

    page_3 = b.Page(
        b.Text(adv_blocks).format(plots=plots, tables=tables, text=text, embed=embed, files=files), label="Blocks"
    )

    return Report(page_1, page_2, page_3)
