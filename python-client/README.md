<p align="center">
  <a href="https://datapane.com">
    <img src="https://cloud.datapane.com/static/datapane-logo-dark.png" width="250px" alt="Datapane" />
  </a>
</p>
<p align="center">
  <a href="https://datapane.com/cloud">Cloud</a> |
  <a href="https://docs.datapane.com">Docs</a> |
      <a href="#demos-and-examples">Examples</a> |
  <a href="https://datapane.nolt.io">Roadmap</a> | <a href="https://forum.datapane.com">Forum</a> |
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
  <h1 align='center'>From notebook to shareable data app in 10 seconds.</h1>
</p>
Datapane is a python framework that makes it super easy to build, host, and share interactive data apps straight from your Jupyter notebook.
<br>
<br>
<br>

<p align="center">
  <a href="https://datapane.com">
    <img src="https://user-images.githubusercontent.com/3541695/176545400-919a327d-ddee-4755-b29f-bf85fbfdb4ef.png"  width='75%'>
  </a>
</p>

### What makes Datapane special?

- **Static generation:** Sharing an app shouldn't require deploying an app. Render a standalone HTML bundle which you can share or host on the web.
- **API-first and programmatic:** Programmatically generate apps from inside of Spark, Airflow, or Jupyter. Schedule updates to build real-time dashboards.
- **Dynamic front-end components**: Say goodbye to writing HTML. Build apps from a set of interactive components, like DataTables, tabs, and selects.

# Getting Started

Want a head start? Check out our _Datapane in 3 minutes_ video:

https://user-images.githubusercontent.com/15690380/179759362-e577a4f8-d1b7-4b8d-9190-0c13d5015728.mp4

## Installing Datapane

The best way to install Datapane is through pip or conda.

#### pip

```
$ pip3 install -U datapane
```

#### conda

```
$ conda install -c conda-forge "datapane>=0.15.5"
```

Datapane also works well in hosted Jupyter environments such as Colab or Binder, where you can install as follows:

```
!pip3 install --quiet datapane
```

# Creating apps

### 📊 Include plots and data

Create an app from pandas DataFrames, plots from your favorite libraries, and text.

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
app = dp.App(
    dp.Plot(fig),
    dp.DataTable(df)
)
app.save(path="my_app.html")
```

</p>

### 🎛 Layout using interactive blocks

Add dropdowns, selects, grid, pages, and 10+ other blocks to enhance your apps.

<p>

<img width='485px' align='left' alt="Complex layout" src="https://user-images.githubusercontent.com/3541695/176288321-44f7e76f-5032-434b-a3b0-ed7e3911b5d5.png">

<p >

```python


...

dp.App(
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
).save(path="layout_example.html")

```

</p>
</p>

<br>
<br>
<br>

# Get involved

## Discord

Our Discord community is for people who believe that insights, visualizations, and apps are better created with Python instead of drag-and-drop tools. Get help from the team, share what you're building, and get to know others in the space!

### 💬 [Join our discord server](https://chat.datapane.com)

## Feedback

Leave us some feedback, ask questions and request features.

### 📮 [Give feedback](https://datapane.nolt.io)

## Forums

Need technical help? Ask our experts on the forums.

### 📜 [Ask a question](https://forum.datapane.com/)

## Contribute

Looking for ways to contribute to Datapane?

### ✨ [Visit the contribution guide](https://github.com/datapane/datapane/blob/main/CONTRIBUTING.md).

# Hosting Apps

In addition to saving apps locally or hosting them yourself, you can host and share your apps using [Datapane Cloud](https://datapane.com/cloud).

To get your API key, [create a free account](https://cloud.datapane.com/accounts/signup/).

Next, in your Python notebook or script, change the `save` function to `upload`:

```python
dp.App(
 ...
#).save(path="hello_world.html")
).upload(name="Hello world")
```

# Demos and Examples

Here a few samples of the top apps created by the Datapane community.

- [Coindesk analysis](https://cloud.datapane.com/apps/wAwZqpk/initial-coindesk-article-data/) by Greg Allan
- [COVID-19 Trends by Quarter](https://cloud.datapane.com/apps/q34yW57/covid-19-trends-by-quarter-with-data-through-march-2021/) by Keith Johnson
- [Ecommerce Report](https://cloud.datapane.com/apps/dA9yQwA/e-commerce-report/) by Leo Anthias
- [Example Academic Paper](https://cloud.datapane.com/apps/wAwneRk/towards-orientation-invariant-sensorimotor-object-recognition-based-on-hierarchical-temporal-memory-with-cortical-grid-cells/) by Kalvyn Roux
- [Exploration of Restaurants in Kyoto](https://cloud.datapane.com/apps/0kz48Y3/exploration-of-restaurants-in-kyoto-and-the-stations-theyre-closest-to/) by Ryan Hildebrandt

# Next Steps

- [Join Discord](https://chat.datapane.com)
- [Sign up for a free account](https://datapane.com/accounts/signup)
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
$ mkdir -p ~/Library/Application\ Data/datapane && touch ~/Library/Application\ Data/no_analytics
```

### Windows (PowerShell)

```powershell
PS> mkdir ~/AppData/Roaming/datapane -ea 0
PS> ni ~/AppData/Roaming/datapane/no_analytics -ea 0
```

You may need to try `~/AppData/Local` instead of `~/AppData/Roaming` on certain Windows configurations depending on the type of your user-account.
