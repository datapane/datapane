<p align="center">
  <a href="https://datapane.com">
    <img src="https://datapane-cdn.com/static/v1/datapane-logo-dark.svg.br" width="250px" alt="Datapane" />
  </a>
</p>
<p align="center">
  <a href="https://docs.datapane.com">Docs</a> |
  <a href="https://datapane.com/cloud">Cloud</a> |
 <a href="https://forum.datapane.com">Discussions</a> |
  <a href="https://chat.datapane.com">Discord</a>
</p>
<p align='center'>
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
  <h1 align='center'>Build full-stack data analytics apps in Python</h1>
</p>
Datapane is an open-source framework for building robust, high-performance data apps from Python and Jupyter.
<br><br>
<br>
<br>

<p align="center">
  <a href="https://datapane.com">
    <img src="https://user-images.githubusercontent.com/3541695/176545400-919a327d-ddee-4755-b29f-bf85fbfdb4ef.png"  width='75%'>
  </a>
</p>

## Why use Datapane?

#### **🚀 Not just for demos**

Build performant, robust full-stack apps which are simple to deploy and manage on any hosting platform. Add background processing, auth, and monitoring to go beyond MVPs.

#### **📈 Share standalone reports with no server**

Export static HTML reports which you can share on Slack or Email, with no backend required.

#### **📙 Ship apps from Jupyter**

Build and ship data apps from inside your Jupyter Notebook and existing scripts in <5 lines of code.

## Other Features

- User sessions and state handling
- Intelligent caching
- Sub-5ms function response time
- Easy integration with authentication/authorization
- Integrate into existing web frameworks (like Flask or FastAPI)
- Host on existing web-hosts, like Fly and Heroku
- Background processing

## How is Datapane's architecture unique?

Datapane Apps use a combination of pre-rendered frontend elements and backend Python functions which are called on-demand. Result: low-latency apps which are simple to build, host, and scale.

# Getting Started

Want a head start? Check out our [Getting Started guide](TODO) to build a data science web app in 3m.

## Installing Datapane

The best way to install Datapane is through pip or conda.

#### pip

```
$ pip3 install -U datapane
```

#### conda

```
$ conda install -c conda-forge "datapane>=0.15.6"
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

## Discord

Get help from the team, share what you're building, and get to know others in the space!

### 💬 [Join our discord server](https://chat.datapane.com)

## Feedback

Leave us some feedback, ask questions and request features.

### 📮 [Give feedback](https://datapane.nolt.io)

## Forums

Need technical help? Reach out on GitHub discussions.

### 📜 [Ask a question](https://forum.datapane.com/)

## Contribute

Looking for ways to contribute to Datapane?

### ✨ [Visit the contribution guide](https://github.com/datapane/datapane/blob/main/CONTRIBUTING.md).

# Next Steps

- [Join Discord](https://chat.datapane.com)
- [Sign up for a free account](https://cloud.datapane.com/accounts/signup)
- [Read the documentation](https://docs.datapane.com)
- [Ask a question](https://forum.datapane.com/)

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
