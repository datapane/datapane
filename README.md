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
</p>

Datapane is a Python library which makes it simple to build reports from the common objects in your data analysis, such as pandas DataFrames, plots from Python visualisation libraries, and Markdown. 

Reports can be exported as standalone HTML documents, with rich components which allow data to be explored and visualisations to be used interactively.

For example, if you wanted to create a report with a table viewer and an interactive plot:

```python
import altair as alt
import pandas as pd
from datapane import LocalReport, Table, Plot
​
df = pd.read_csv('https://query1.finance.yahoo.com/v7/finance/download/GOOG?period1=1553600505&period2=1585222905&interval=1d&events=history')
chart = alt.Chart(df).encode(x='Date', y='High', y2='Low').mark_area(opacity=0.5).interactive()
​
LocalReport.create([
    Table.create(df), 
    Plot.create(chart)
])
```

This would package a standalone HTML report such as the following, with an searchable Table and Plot component.

![Report Example](https://i.imgur.com/RGp7RzM.png)


# Getting Started

- [Read the documentation](https://docs.datapane.com)
- [View samples and demos](https://docs.datapane.com)

# Components

Datapane currently contains the following components. Need something different? Open an issue (or make a PR!) 
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
</p>

Datapane is a Python library which makes it simple to build reports from the common objects in your data analysis, such as pandas DataFrames, plots from Python visualisation libraries, and Markdown. 

Reports can be exported as standalone HTML documents, with rich components which allow data to be explored and visualisations to be used interactively.

For example, if you wanted to create a report with a table viewer and an interactive plot:

```python
import altair as alt
import pandas as pd
from datapane import LocalReport, Table, Plot
​
df = pd.read_csv('https://query1.finance.yahoo.com/v7/finance/download/GOOG?period1=1553600505&period2=1585222905&interval=1d&events=history')
chart = alt.Chart(df).encode(x='Date', y='High', y2='Low').mark_area(opacity=0.5).interactive()
​
LocalReport.create([
    Table.create(df), 
    Plot.create(chart)
])
```

This would package a standalone HTML report such as the following, with an searchable Table and Plot component.

![Report Example](https://i.imgur.com/RGp7RzM.png)


# Getting Started

- [Read the documentation](https://docs.datapane.com)
- [View samples and demos](https://docs.datapane.com)

# Components

Datapane currently contains the following components. Need something different? Open an issue (or make a PR!) 

| Component | Description                                                                    | Supported Formats                                   | Example                                                                         |
|-----------|--------------------------------------------------------------------------------|-----------------------------------------------------|---------------------------------------------------------------------------------|
| Table     | A searchable, sortable table component for datasets. Supports up to 10m cells. | Pandas DataFrames, JSON documents, Local CSV files  | `Table.create(df)`                                                              |
| Plot      | A wrapper for plots from Python visualisation libraries.                       | Altair charts, Bokeh plots, Matplotlib figures, SVG |  ``` plot = alt.Chart(df).encode(x='x',y='y').mark_line() Plot.create(plot) ``` |
| Markdown  | A simple Markdown component to document your report.                           | Markdown, Text                                      | `Markdown("# My fun title")                                                     |

# Datapane.com

In addition to the this local library, Datapane.com provides an API and hosted platform which allows you to:

1. Upload Jupyter Notebooks and Python scripts, so that other people can run them in their browser with parameters to generate reports dynamically
2. Share and embed your script or reports online -- either publicly, or privately within your team

# Mission

Although there are many enterprise BI and reporting tools with drag and drop interfaces, using SQL with Python is often the best combination for querying, analysing, and visualising data. Unfortunately, it can be hard to package and share results in a way that is accessible and friendly to everyone. Datapane's goal is to provide the bridge between where you want to analyse data, and how other people want to interact with it.

# Datapane.com

In addition to the this local library, Datapane.com provides an API and hosted platform which allows you to:

1. Upload Jupyter Notebooks and Python scripts, so that other people can run them in their browser with parameters to generate reports dynamically
2. Share and embed your script or reports online -- either publicly, or privately within your team

# Mission

Although there are many enterprise BI and reporting tools with drag and drop interfaces, using SQL with Python is often the best combination for querying, analysing, and visualising data. Unfortunately, it can be hard to package and share results in a way that is accessible and friendly to everyone. Datapane's goal is to provide the bridge between where you want to analyse data, and how other people want to interact with it.
