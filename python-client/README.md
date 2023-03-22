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
  <h1 align='center'>Build full-stack data apps in 100% Python</h1>
</p>

Datapane is an app development platform which gives you everything you need to build internal data analytics products using Python.

### Progress & Roadmap

- [x] [Blocks & Views](https://docs.datapane.com/blocks/overview/)
  - [x] Display blocks
  - [x] Layout blocks
  - [x] Static site export
- [x] [App server](https://docs.datapane.com/apps/overview/)
  - [x] Backend functions
  - [x] Forms
  - [x] Client-side events (e.g. onload)
  - [x] Caching
  - [x] Sessions
- [x] [Reports](https://docs.datapane.com/reports/overview/)
  - [x] HTML reports
  - [x] Cloud reports
- [x] [Deployment](https://docs.datapane.com/apps/deployment/#deploying-your-app)
  - [x] Fly.io
  - [x] Dockerfile generation
- [x] [Components library](https://github.com/datapane/components)
- [ ] Tasks
  - [ ] Scheduled tasks
  - [ ] Background tasks
- [ ] Data layer
  - [ ] Files
  - [ ] Analytics DB (DuckDB)
  - [ ] App state DB (sqlite)
- [ ] Integrations & Messaging
  - [ ] Slack
  - [ ] Email
  - [ ] Webhooks

## Why use Datapane?

#### **🐍 100% Python**

Build apps and reporting tools without writing HTML, CSS, or worrying about infrastructure.

#### **🔋 Batteries included**

Not just for demos and MVPs. Build products with background processing, integrations, reporting, and more.

#### **🚀 Simple to host**

Deploy to any web host, run on your own server, or embed into existing frameworks like Flask and Django.

## Gallery

Check out example reports and apps in our gallery:

https://datapane.com/gallery

## How is Datapane's architecture unique?

Datapane Apps use a combination of pre-rendered frontend elements and backend Python functions which are called on-demand. Result: low-latency apps which are simple to build, host, and scale.

# Getting Started

Check out our [Quickstart](https://docs.datapane.com/quickstart) to build a data science web app in 3m.

## Installing Datapane

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

# Examples

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

### Add functions to create full-stack apps

Add forms which run backend functions, or refresh your app automatically to build dashboards. Serve locally or deploy to your favorite web-host.

<p>

<img width='485px' align='left' alt="Functions" src="https://user-images.githubusercontent.com/3541695/221241943-dc2a03ae-1fd9-4278-8636-6344c5098a5c.gif">

<p>

```python
import altair as alt
from vega_datasets import data
import datapane as dp

df = data.iris()

def gen_assets(params):
    subset = df[df['species'] == params['species']]

    fig = alt.Chart(subset)
            .mark_point()
            .encode( x="petalLength:Q", y="petalWidth:Q")

    return [dp.Plot(fig), dp.DataTable(subset)]

view = dp.Form(
    on_submit=gen_assets,
    controls=dp.Controls(
      species=dp.Choice(options=list(df['species'].unique())
    )
)

dp.serve_app(view)
```

# Get involved

## Forums

Leave us some feedback, get help, ask questions and request features.

### 📜 [Ask a question](https://forum.datapane.com/)

## Contribute

Looking for ways to contribute to Datapane?

### ✨ [Visit the contribution guide](https://github.com/datapane/datapane/blob/main/CONTRIBUTING.md).

# Next Steps

- [View Examples](https://github.com/datapane/examples)
- [Read the documentation](https://docs.datapane.com)
- [Discuss with the community](https://forum.datapane.com/)
- [Sign up for a free Cloud account](https://cloud.datapane.com/accounts/signup)

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
