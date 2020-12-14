<p align="center">
  <a href="https://datapane.com">
    <img src="https://datapane.com/static/datapane-logo-dark.png" width="250px" alt="Datapane" />
  </a>
</p>
<p align="center">
    <a href="https://datapane.com">Datapane.com</a> |
    <a href="https://docs.datapane.com">Documentation</a> |
    <a href="https://twitter.com/datapaneapp">Twitter</a>
    <br /><br />
    <a href="https://pypi.org/project/datapane/">
        <img src="https://img.shields.io/pypi/dm/datapane?label=pip%20downloads" alt="Pip Downloads" />
    </a>
    <a href="https://pypi.org/project/datapane/">
        <img src="https://img.shields.io/pypi/v/datapane?color=blue" alt="Latest release" />
    </a>
    <a href="https://anaconda.org/conda-forge/datapane">
        <img src="https://anaconda.org/conda-forge/datapane/badges/version.svg" alt="Latest release" />
    </a>
    <img src="https://github.com/datapane/datapane-hosted/workflows/Test%20%5BDP%20CLI%5D/badge.svg" alt="Latest release" />
</p>

Datapane is a Python library which makes it simple to build reports from the common objects in your data analysis, such as pandas DataFrames, plots from Python visualisation libraries, and Markdown.

Reports can be exported as standalone HTML documents, with rich components which allow data to be explored and visualisations to be used interactively.

For example, if you wanted to create a report with a table viewer and an interactive plot:

```python
import pandas as pd
import altair as alt
import datapane as dp

df = pd.read_csv('https://query1.finance.yahoo.com/v7/finance/download/GOOG?period2=1585222905&interval=1mo&events=history')

chart = alt.Chart(df).encode(
    x='Date:T',
    y='Open'
).mark_line().interactive()

r = dp.Report(dp.DataTable(df), dp.Plot(chart))
r.save(path='report.html', open=True)
```

This would package a standalone HTML report such as the following, with an searchable Table and Plot component.

![Report Example](https://i.imgur.com/RGp7RzM.png)

# Getting Started

- [Read the documentation](https://docs.datapane.com)
- [View samples and demos](https://github.com/datapane/datapane-demos/)

# Components

Datapane currently contains the following components. Need something different? Open an issue (or make a PR!)

| Component | Description                                                                    | Supported Formats                                  | Example                      |
| --------- | ------------------------------------------------------------------------------ | -------------------------------------------------- | ---------------------------- |
| Table     | A searchable, sortable table component for datasets. Supports up to 10m cells. | Pandas DataFrames, JSON documents, Local CSV files | `Table(df)`                  |
| Plot      | A wrapper for plots from Python visualisation libraries.                       | Altair, Bokeh, Matplotlib, SVG                     | `Plot(altair_chart)`         |
| Markdown  | A simple Markdown component to document your report.                           | Markdown, Text                                     | `Markdown("# My fun title")` |

# Datapane.com

In addition to the this local library, Datapane.com provides an API and hosted platform which allows you to:

1. Upload Jupyter Notebooks and Python scripts, so that other people can run them in their browser with parameters to generate reports dynamically
1. Share and embed reports online -- either publicly, or privately within your team

# Joining the community

Looking to get answers to questions or engage with us and the wider community? Our community is most active on our Discourse Forum. Submit requests, issues, and bug reports on this GitHub repo, or join us by contributing on some good first issues on this repo.

We look forward to building an amazing open source community with you!
