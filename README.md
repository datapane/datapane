<p align="center">
  <a href="https://datapane.com">
    <img src="https://datapane.com/static/datapane-logo-dark.png" width="250px" alt="Datapane" />
  </a>
</p>
<p align="center">
    <a href="https://datapane.com">Datapane Teams</a> |
    <a href="https://docs.datapane.com">Documentation</a> |
    <a href="https://datapane.github.io/datapane/">API Docs</a> |
    <a href="https://docs.datapane.com/changelog">Changelog</a> |
    <a href="https://twitter.com/datapaneapp">Twitter</a> |
    <a href="https://blog.datapane.com">Blog</a>
    <br /><br />
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
<h4>Share interactive plots and data in 3 lines of Python.</h4>

Datapane is a Python library for building interactive reports for your end-users in seconds.

Import our library into your existing script/notebook and build reports from pandas Dataframes, plots from Python viz libraries, Markdown, as well as data exploration and layout components.

Export your reports as standalone HTML documents, or share and embed them via our free hosted platform.

# Getting Started

## Installing Datapane

The best way to install Datapane is through pip or conda.

#### pip

```
$ pip3 install -U datapane
$ datapane hello-world
```

#### conda

```
$ conda install -c conda-forge "datapane>=0.12.0"
$ datapane hello-world
```

Datapane also works well in hosted Jupyter environments such as Colab or Binder, where you can install as follows:

```
!pip3 install --quiet datapane
!datapane signup
```

## Explainer Video

https://user-images.githubusercontent.com/16949044/134007757-0b91074a-2b32-40ba-b385-5623dff8c04e.mp4

## Hello world

Let's say you wanted to create a report with an interactive plot and table viewer:

```python
import altair as alt
from vega_datasets import data
import datapane as dp

source = data.cars()

plot1 = alt.Chart(source).mark_circle(size=60).encode(
  x='Horsepower',
  y='Miles_per_Gallon',
  color='Origin',
  tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
).interactive()

dp.Report(
    dp.Text("## Hello world!"),
    dp.Plot(plot1),
    dp.DataTable(source)
).save(path="Hello_world.html")
```

This will package a standalone HTML document that looks as follows:

<img width="1269" alt="Simple Datapane report example with text, plot and table" src="https://user-images.githubusercontent.com/16949044/134021084-39b3369b-3c42-478c-b1fb-79f2b5b4b4a2.png">

Your users can scroll & zoom on the chart, filter and download the tabular data.

## Advanced Layout Options

Datapane is great for presenting complex data and provides many components for creating advanced interactive layouts. Let's you need to write a technical document:

```python
import altair as alt
from vega_datasets import data
import datapane as dp

source = data.cars()
plot1 = alt.Chart(source).mark_circle(size=60).encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
    tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
).interactive()

dp.Report(
    dp.Page(title="Charts and analysis",
            blocks=[
                dp.Formula("x^2 + y^2 = z^2"),
                dp.Group(
                    dp.BigNumber(
                        heading="Number of percentage points",
                        value="84%",
                        change="2%",
                        is_upward_change=True
                    ),
                    dp.BigNumber(
                        heading="Simple Statistic",
                        value=100
                    ), columns=2,
                ),
                dp.Select(blocks=[
                    dp.Plot(plot1, label="Plot"),
                    dp.HTML('''<iframe width="560" height="315" src="https://www.youtube.com/embed/dQw4w9WgXcQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>''', label="Video")
                ]),
            ]),
    dp.Page(title="Dataset", blocks=[
            dp.DataTable(source)
    ])
).save(path="Complex_layout.html", open=True)
```

Layout blocks like `dp.Select`, `dp.Group` and `dp.Page` allow you to highlight key points without sacrificing detail, while content blocks like `dp.HTML` and `dp.Formula` (LaTeX) can enrich your report. The final result looks like this:

<img width="1000" alt="Complex Datapane report example" src="https://user-images.githubusercontent.com/16949044/134022445-5d417993-808f-4de8-8e8c-f510bdf4a17e.png">

Check out the full list of blocks in our [documentation](https://docs.datapane.com/reports/blocks).

# Sharing Reports

## Sign up for a free account

In addition to saving documents locally, you can host, share and embed reports via [Datapane Studio](https://datapane.com/).

To get your free API key, run the following command in your terminal to sign up via email/OAuth:

```
$ datapane signup
```

If you're using Jupyter, run `!datapane signup` instead.

Next, in your Python notebook or script simply change the `save` function to `upload` on your report:

```python
dp.Report(
 ...
#).save(path="hello_world.html")
).upload(name="Hello world")
```

Your Studio account comes with the following:

- **Unlimited public reports** - great for embedding into places like Medium, Reddit, or your own website (see [here](https://docs.datapane.com/reports/embedding-reports-in-social-platforms))
- **5 private reports** - share these via email within your organization

### Featured Examples

Here a few samples of the top reports created by the Datapane community. To see more, check out our [gallery](https://datapane.com/gallery) section.

- [Tutorial Report](https://datapane.com/u/leo/reports/tutorial-1/) by Datapane Team
- [Coindesk analysis](https://datapane.com/u/greg/reports/initial-coindesk-article-data/) by Greg Allan
- [COVID-19 Trends by Quarter](https://datapane.com/u/keith8/reports/covid-19-trends-by-quarter/) by Keith Johnson
- [Ecommerce Report](https://datapane.com/u/leo/reports/e-commerce-report/) by Leo Anthias
- [Example Academic Paper](https://datapane.com/u/kalru/reports/supplementary-material/) by Kalvyn Roux
- [Exploration of Restaurants in Kyoto](https://datapane.com/u/ryancahildebrandt/reports/kyoto-in-stations-and-restaurants/) by Ryan Hildebrandt

# Teams

[Datapane Teams](https://datapane.com/teams/) is our plan for teams, which adds the following features on top of our open-source and Studio plans:

- Private domain and organizational workspace
- Multiple projects
- Client-sharing functionality
- Unlimited Datapane Apps
- Custom App packages and environments
- Secure Warehouse & API Integration
- File and Dataset APIs
- Private Slack or Teams support

Datapane Teams is offered as both a managed SaaS service and an on-prem install. For more information, see [the documentation](https://docs.datapane.com/datapane-teams/tut-deploying-a-script). You can find pricing [here](https://datapane.com/pricing).

## Next Steps

- [Sign up for a free account](https://datapane.com/accounts/signup)
- [Read the documentation](https://docs.datapane.com)
- [Browse the API docs](https://datapane.github.io/datapane/)
- [View featured reports](https://github.com/datapane/gallery/)

# Analytics

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

## Joining the community

Looking to get answers to questions or engage with us and the wider community? Check out our [GitHub Discussions](https://github.com/datapane/datapane/discussions) board.

Submit feature requests, issues, and bug reports on this GitHub repo.

## Open-source, not open-contribution

Datapane is currently closed to external code contributions. However, we are tremendously grateful to the community for any feature requests, ideas, discussions, and bug reports.
