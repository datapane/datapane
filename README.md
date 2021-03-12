<p align="center">
  <a href="https://datapane.com">
    <img src="https://datapane.com/static/datapane-logo-dark.png" width="250px" alt="Datapane" />
  </a>
</p>
<p align="center">
    <a href="https://datapane.com">Datapane.com</a> |
    <a href="https://datapane.com/enterprise">Datapane Enterprise</a> |
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

Datapane is a Python library which makes it simple to build reports from the common objects in your data analysis, such as pandas DataFrames, plots from Python visualisation libraries, and Markdown.

Reports can be exported as standalone HTML documents, with rich components which allow data to be explored and visualisations to be used interactively.

For example, if you wanted to create a report with a table viewer and an interactive plot:

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

This would package a standalone HTML report such as the following, with a searchable DataTable and Plot component.

![Report Example](https://imgur.com/PTiSCM0.png)

# Getting Started

## Install

- `pip3 install datapane` OR
- `conda install -c conda-forge "datapane>=0.10.0"`

## Next Steps

- [Read the documentation](https://docs.datapane.com)
- [Browse the API docs](https://datapane.github.io/datapane/)
- [Browse samples and demos](https://github.com/datapane/gallery/)
- [View featured reports](https://datapane.com/explore/?tab=featured)

# Datapane.com

In addition to saving reports locally, [Datapane](datapane.com) provides a free hosted platform and social network at https://datapane.com, including the following features:

- published reports can kept private and securely shared,
- reports can be shared publicly and become a part of the wider data stories community,
- report embedding within your blogs, CMSs, and elsewhere (see [here](https://docs.datapane.com/reports/embedding-reports-in-social-platforms)),
- explorations and integrations, e.g. additional DataTable analysis features and [GitHub action](https://github.com/datapane/build-action) integration.

It's super simple, just login (see [here](https://docs.datapane.com/tut-getting-started#authentication)) and call the `publish` function on your report,

```python
r = dp.Report(dp.DataTable(df), dp.Plot(chart))
r.publish(name="2020 Stock Portfolio", open=True)
```

# Enterprise

[Datapane Enterprise](https://datapane.com/enterprise/) provides automation and secure sharing of reports within in your organization.

- Private report sharing within your organization and within groups, including external clients
- Deploy Notebooks and scripts as automated, parameterised reports that can be run by your team interactively
- Schedule reports to be generated and shared
- Runs managed or on-prem
- [and more](<(https://datapane.com/enterprise/)>)

# Joining the community

Looking to get answers to questions or engage with us and the wider community? Check out our [GitHub Discussions](https://github.com/datapane/datapane/discussions) board.

Submit requests, issues, and bug reports on this GitHub repo.

We look forward to building an amazing open source community with you!
