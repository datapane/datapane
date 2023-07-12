<p align="center">
  <a href="https://datapane.com">
    <img src="https://datapane-cdn.com/static/v1/datapane-logo-dark.svg.br" width="250px" alt="Datapane" />
  </a>
</p>
<p align="center">
  <a href="https://datapane.com">Home</a> |
  <a href="https://docs.datapane.com">Docs</a> |
  <a href="https://datapane.com/gallery">Gallery</a> |
  <a href="https://github.com/datapane/examples">Examples</a> |
  <a href="https://forum.datapane.com">Discuss</a>
</p>
<p align='center'>
  <a href="https://github.com/datapane/datapane/">
      <img src="https://img.shields.io/github/stars/datapane/datapane?style=social" alt="GitHub Stars" />
  </a>
  <a href="https://pypi.org/project/datapane/">
      <img src="https://img.shields.io/pypi/dm/datapane?label=pip%20downloads" alt="Pip Downloads" />
  </a>
  <a href="https://pypi.org/project/datapane/">
      <img src="https://img.shields.io/pypi/v/datapane?color=blue" alt="Latest release" />
  </a>
  <a href="https://anaconda.org/conda-forge/datapane">
      <img alt="Conda (channel only)" src="https://img.shields.io/conda/vn/conda-forge/datapane">
  </a>
</p>

<p align='center'>
  <h1 align='center'>Build interactive reports in seconds using Python.</h1>
</p>

Datapane makes it simple to build interactive reports in seconds using Python.

Import Datpane's Python library into your script or notebook and build reports programmatically by wrapping components such as:

- Pandas DataFrames
- Plots from Python visualization libraries such as Bokeh, Altair, Plotly, and Folium
- Markdown and text
- Files, such as images, PDFs, JSON data, etc.
- Interactive forms which run backend Python functions

Datapane reports are interactive and can also contain pages, tabs, drop downs, and more. Once created, reports can be exported as HTML, shared as standalone files, or embedded into your own application, where your viewers can interact with your data and visualizations.

## Gallery

Check out example reports in our gallery and view their source:

- https://datapane.com/gallery
- https://github.com/datapane/examples

## Getting Started

Check out our [Quickstart](https://docs.datapane.com/quickstart) to build a report in 3m.

### Installing Datapane

The best way to install Datapane is through pip or conda.

#### pip

```
$ pip3 install -U datapane
```

#### conda

```
$ conda install -c conda-forge "datapane>=0.16.1"
```

Datapane also works well in hosted Jupyter environments such as Colab or Binder, where you can install as follows:

```
!pip3 install --quiet datapane
```

## Examples

### 📊 Share plots, data, and more as reports

Create reports from pandas DataFrames, plots from your favorite libraries, and text.

<p>

<img width='485px' align='left' alt="Simple Datapane app example with text, plot and table" src="https://user-images.githubusercontent.com/3541695/176251650-f49ea9f8-3cd4-4eda-8e78-ccba77e8e02f.png">

<p>

```python
import altair as alt
from vega_datasets import data
import datapane as dp

df = data.iris()
fig = (
    alt.Chart(df)
    .mark_point()
    .encode(
        x="petalLength:Q",
        y="petalWidth:Q",
        color="species:N"
    )
)
view = dp.Blocks(
    dp.Plot(fig),
    dp.DataTable(df)
)
dp.save_report(view, path="my_app.html")
```

</p>

### 🎛 Layout using interactive blocks

Add dropdowns, selects, grid, pages, and 10+ other interactive blocks.

<p>

<img width='485px' align='left' alt="Complex layout" src="https://user-images.githubusercontent.com/3541695/176288321-44f7e76f-5032-434b-a3b0-ed7e3911b5d5.png">

<p>

```python
...

view = dp.Blocks(
    dp.Formula("x^2 + y^2 = z^2"),
    dp.Group(
        dp.BigNumber(
            heading="Number of percentage points",
            value="84%",
            change="2%",
            is_upward_change=True
        ),
        dp.BigNumber(
            heading="Simple Statistic", value=100
        ), columns=2
    ),
    dp.Select(
        dp.Plot(fig, label="Chart"),
        dp.DataTable(df, label="Data")
    ),
)
dp.save_report(view, path="layout_example.html")
```

## Next Steps

- [Quickstart](https://docs.datapane.com/quickstart) - build a report in 3m
- [Visit our Forums](https://forum.datapane.com/) - leave feedback, get help, ask questions and request features
- [View Examples](https://github.com/datapane/examples)
- [Read the documentation](https://docs.datapane.com)

## Analytics

By default, the Datapane Python library collects error reports and usage telemetry.
This is used by us to help make the product better and to fix bugs.
If you would like to disable this, simply create a file called `no_analytics` in your `datapane` config directory, e.g.

### Linux

```bash
$ mkdir -p ~/.config/datapane && touch ~/.config/datapane/no_analytics
```

### macOS

```bash
$ mkdir -p ~/Library/Application\ Support/datapane && touch ~/Library/Application\ Support/datapane/no_analytics
```

### Windows (PowerShell)

```powershell
PS> mkdir ~/AppData/Roaming/datapane -ea 0
PS> ni ~/AppData/Roaming/datapane/no_analytics -ea 0
```

You may need to try `~/AppData/Local` instead of `~/AppData/Roaming` on certain Windows configurations depending on the type of your user-account.
