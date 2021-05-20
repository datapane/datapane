<p align="center">
  <a href="https://datapane.com">
    <img src="https://datapane.com/static/datapane-logo-dark.png" width="250px" alt="Datapane" />
  </a>
</p>
<p align="center">
    <a href="https://datapane.com">Datapane Cloud</a> |
    <a href="https://docs.datapane.com">Documentation</a> |
    <a href="https://datapane.github.io/datapane/">API Docs</a> |
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
<h4>Turn a Python analysis into a beautiful document in 3 lines of code.
</h1>

Datapane is a Python library which makes it simple to build reports from the common objects in your data analysis, such as pandas DataFrames, plots from Python visualisation libraries, and Markdown.

Reports can be exported as standalone HTML documents, with rich components which allow data to be explored and visualisations to be used interactively. You can also publish reports to our free public community platform or share them securely with your team and clients.

# Getting Started

## Installing Datapane

The best way to install Datapane is through pip or conda.

#### pip

`pip3 install -U datapane`

#### conda

`conda install -c conda-forge "datapane>=0.10.0"`

Datapane also works well in hosted Jupyter environments such as Colab or Binder, where you can install as follows:

`!pip3 install --quiet datapane`

## Explainer Video

https://user-images.githubusercontent.com/3541695/117458709-7e80ba80-af42-11eb-9fa7-a11bb05229fe.mp4

## Hello world

Let's say you wanted to create a document with a table viewer and an interactive plot:

```python
import pandas as pd
import altair as alt
import datapane as dp

df = pd.read_csv('https://covid.ourworldindata.org/data/vaccinations/vaccinations-by-manufacturer.csv', parse_dates=['date'])
df = df.groupby(['vaccine', 'date'])['total_vaccinations'].sum().reset_index()

plot = alt.Chart(df).mark_area(opacity=0.4, stroke='black').encode(
    x='date:T',
    y=alt.Y('total_vaccinations:Q'),
    color=alt.Color('vaccine:N', scale=alt.Scale(scheme='set1')),
    tooltip='vaccine:N'
).interactive().properties(width='container')

total_df = df[df["date"] == df["date"].max()].sort_values("total_vaccinations", ascending=False).reset_index(drop=True)
total_styled = total_df.style.bar(subset=["total_vaccinations"], color='#5fba7d', vmax=total_df["total_vaccinations"].sum())

dp.Report("## Vaccination Report",
    dp.Plot(plot, caption="Vaccinations by manufacturer over time"),
    dp.Table(total_styled, caption="Current vaccination totals by manufacturer")
).save(path='report.html', open=True)
```

This would package a standalone HTML report document such as the following:

![Report Example](https://user-images.githubusercontent.com/3541695/117442319-82a2dd00-af2e-11eb-843e-29097f425a55.png)

## Featured Examples

Here a few samples of the top reports created by the Datapane community. To see more, see our [featured](https://datapane.com/featured) section.

- [Tutorial Report](https://datapane.com/u/leo/reports/tutorial-1/) by Datapane Team
- [Coindesk analysis](https://datapane.com/u/greg/reports/initial-coindesk-article-data/) by Greg Allan
- [COVID-19 Trends by Quarter](https://datapane.com/u/keith8/reports/covid-19-trends-by-quarter/) by Keith Johnson
- [Ecommerce Report](https://datapane.com/u/leo/reports/e-commerce-report/) by Leo Anthias
- [Example Academic Paper](https://datapane.com/u/kalru/reports/supplementary-material/) by Kalvyn Roux
- [Example Sales Report](https://datapane.com/u/datapane/reports/sample-internal-report/) by Datapane Team
- [Example Client Report](https://datapane.com/u/datapane/reports/sample-external-report/) by Datapane Team
- [Exploration of Restaurants in Kyoto](https://datapane.com/u/ryancahildebrandt/reports/kyoto-in-stations-and-restaurants/) by Ryan Hildebrandt
- [The Numbers on Particles](https://datapane.com/u/ryancahildebrandt/reports/the-numbers-on-particles/) by Ryan Hildebrandt

## Next Steps

- [Read the documentation](https://docs.datapane.com)
- [Browse the API docs](https://datapane.github.io/datapane/)
- [Browse samples and demos](https://github.com/datapane/gallery/)
- [View featured reports](https://datapane.com/explore/?tab=featured)

# Sharing Reports

## Public sharing

In addition to saving documents locally, you can use [Datapane Community](https://datapane.com/explore) to publish your reports. Datapane Community is a free hosted platform which is used by tens of thousands of people each month to view and share Python reports.

- Reports can be published for free and shared publicly
- You can embed them into places like Medium, Reddit, or your own website (see [here](https://docs.datapane.com/reports/embedding-reports-in-social-platforms))
- Viewers can explore and download your data with additional DataTable analysis features

To get started, create a free API key (see [here](https://docs.datapane.com/tut-getting-started#authentication)) and call the `publish` function on your report,

```python
r = dp.Report(dp.DataTable(df), dp.Plot(chart))
r.publish(name="2020 Stock Portfolio", open=True)
```

## Private sharing

If you need private report sharing, [Datapane Cloud](https://docs.datapane.com/datapane-enterprise/) allows secure sharing of reports and the ability to deploy your Jupyter Notebooks or Python scripts as interactive apps.

- Share reports privately with your company or external clients
- Deploy Jupyter Notebooks and scripts as apps, with inputs that can be run by your team interactively to dynamically create results
- Schedule reports to automatically update

Datapane Cloud is offered as both a managed SaaS service and an on-prem install. For more information, see [the documentation](https://docs.datapane.com/datapane-enterprise/tut-deploying-a-script). You can find pricing [here](https://datapane.com/pricing).

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

# Joining the community

Looking to get answers to questions or engage with us and the wider community? Check out our [GitHub Discussions](https://github.com/datapane/datapane/discussions) board.

Submit feature requests, issues, and bug reports on this GitHub repo.

## Open-source, not open-contribution

Datapane is currently closed to external code contributions. However, we are tremendously grateful to the community for any feature requests, ideas, discussions, and bug reports.
