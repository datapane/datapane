<p align="center">
  <a href="https://datapane.com">
    <img src="https://datapane.com/static/datapane-logo-dark.png" width="250px" alt="Datapane" />
  </a>
</p>
<p align="center">
  <a href="https://datapane.com">Datapane.com</a> |
  <a href="https://docs.datapane.com">Docs</a> |
      <a href="https://datapane.com/showcase">Examples</a> |
  <a href="https://forum.datapane.com">Forums</a>   | <a href="https://chat.datapane.com">Discord</a>
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
  <h1 align='center'> Build interactive reports in 3 lines of Python</h1>
</p>
Datapane is an open-source framework makes it easy to create beautiful reports from anywhere you can run Python.
Love analyzing data in Python but struggle to share results and insights? Datapane is for you!
<br>
<br>
<br>

<p align="center">
  <a href="https://datapane.com">
    <img src="https://user-images.githubusercontent.com/3541695/176545400-919a327d-ddee-4755-b29f-bf85fbfdb4ef.png"  width='75%'>
  </a>
</p>

### What makes Datapane special?

-   **Static generation:** Sharing a report shouldn't require deploying an app. Render a standalone HTML bundle which you can share or host on the web.
-   **API-first and programmatic:** Programmatically generate reports from inside of Spark, Airflow, or Jupyter. Schedule updates to build real-time dashboards.
-   **Dynamic front-end components**: Say goodbye to writing HTML. Build reports from a set of interactive components, like DataTables, tabs, and selects.

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
$ conda install -c conda-forge "datapane>=0.14.0"
```

Datapane also works well in hosted Jupyter environments such as Colab or Binder, where you can install as follows:

```
!pip3 install --quiet datapane
```

# Creating reports

### 📊 Include plots and data

Create a report from pandas DataFrames, plots from your favorite libraries, and text.

<p>

<img width='485px' align='left' alt="Simple Datapane report example with text, plot and table" src="https://user-images.githubusercontent.com/3541695/176251650-f49ea9f8-3cd4-4eda-8e78-ccba77e8e02f.png">

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
report = dp.Report(
    dp.Plot(fig),
    dp.DataTable(df)
)
report.save(path="my_report.html")
```

</p>

### 🎛 Layout using interactive blocks

Add dropdowns, selects, grid, pages, and 10+ other blocks to make your reports dynamic.

<p>

<img width='485px' align='left' alt="Complex layout" src="https://user-images.githubusercontent.com/3541695/176288321-44f7e76f-5032-434b-a3b0-ed7e3911b5d5.png">

<p >

```python


...

dp.Report(
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
).save(path="Layout_example.html")

```

</p>
</p>

<br>
<br>
<br>

# Get involved

## Discord

Our Discord community is for people who believe that insights, visualizations, and reports are better created with Python instead of drag-and-drop tools. Get help from the team, share what you're building, and get to know others in the space!

### 💬 [Join our discord server](https://chat.datapane.com)

## Forums

Got feature requests, feedback, or questions? Visit our Forum.

### 📮 [Join our forum](https://forum.datapane.com/)

# Hosting Reports

In addition to saving documents locally or hosting them yourself, you can host and share your reports using [Datapane Cloud](https://datapane.com/cloud).

To get your API key, [create a free account](https://datapane.com/accounts/signup/).

Next, in your Python notebook or script, change the `save` function to `upload`:

```python
dp.Report(
 ...
#).save(path="hello_world.html")
).upload(name="Hello world")
```

# Demos and Examples

Here a few samples of the top reports created by the Datapane community.

-   [Coindesk analysis](https://datapane.com/u/greg/reports/initial-coindesk-article-data/) by Greg Allan
-   [COVID-19 Trends by Quarter](https://datapane.com/u/keith8/reports/covid-19-trends-by-quarter/) by Keith Johnson
-   [Ecommerce Report](https://datapane.com/u/leo/reports/e-commerce-report/) by Leo Anthias
-   [Example Academic Paper](https://datapane.com/u/kalru/reports/supplementary-material/) by Kalvyn Roux
-   [Exploration of Restaurants in Kyoto](https://datapane.com/u/ryancahildebrandt/reports/kyoto-in-stations-and-restaurants/) by Ryan Hildebrandt

# Next Steps

-   [Join Discord](https://chat.datapane.com)
-   [Sign up for a free account](https://datapane.com/accounts/signup)
-   [Read the documentation](https://docs.datapane.com)

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
