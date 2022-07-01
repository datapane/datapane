# Welcome to the Datapane documentation!


---
description: High-level introduction to Datapane
---

# Welcome to Datapane

## What is Datapane?

Datapane is a Python library for building interactive reports for your end-users in seconds.&#x20;

Import our library into your existing script/notebook and build reports programmatically by wrapping components such as:

* [Pandas DataFrames](https://pandas.pydata.org/)
* Plots from Python visualization libraries such as [Bokeh](https://bokeh.org/), [Altair](https://altair-viz.github.io/), [Plotly](https://plotly.com/python/), and [Folium](https://python-visualization.github.io/folium/quickstart.html)
* Markdown and text
* General files, such as images, PDFs, JSON data, etc.

Datapane reports are flexible and can also contain pages, tabs, drop downs, and more. Once created, reports can be uploaded to the web, dynamically generated in the cloud, or embedded into your own application, where your viewers can interact with your data and visualizations.&#x20;

Here's an example of a basic Datapane report exported to a HTML document:&#x20;

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

![A HTML report](.gitbook/assets/oss\_screenshot.png)

{% hint style="info" %}
These docs include tutorials and guides on how to use Datapane effectively.&#x20;

API docs describing the Python API for building Datapane Reports, along with additional information on the Datapane Teams API can be found at [https://datapane.github.io/datapane/](https://datapane.github.io/datapane/)
{% endhint %}

## Datapane Studio

{% content-ref url="reports/publishing-and-sharing/" %}
[publishing-and-sharing](reports/publishing-and-sharing/)
{% endcontent-ref %}

If you want to share your report on the web, _Datapane Studio_ provides a free API and hosted platform for uploading and sharing reports. If you have already [created an account and are signed in](tut-getting-started.md#authentication), you can upload your report in a single Python command:

```python
dp.Report(
    dp.Plot(plot), 
    dp.DataTable(df)
).upload(name='Vaccination Report', open=True)  # upload & open report in the browser
```

Once uploaded, you can share your report with your community, class, or friends by sharing the link.

![A published report on Datapane - easy to share privately or publicly](.gitbook/assets/dp-screenshot.png)

In addition, you can embed your uploaded report into social platforms, like Reddit and Medium, where your readers can explore your data and plots interactively without leaving your content, like this:

{% embed url="https://datapane.com/u/datapane/reports/covid-vaccinations/" %}
Live embedded Datapane report
{% endembed %}

{% hint style="info" %}
Your free Studio account comes with an unlimited number of public reports, and 5 private reports so you can test it within your organization. If you need more private reports, [contact us](mailto:support@datapane.com) or try our Enterprise product (read on)
{% endhint %}

## Datapane Teams

{% content-ref url="broken-reference" %}
[Broken link](broken-reference)
{% endcontent-ref %}

If your team is using the Python data stack for analysis and visualization, but is still relying on a drag-and-drop BI tool to share results, _Datapane Teams_ provides an API-first way to share reports directly from Python. This enables data teams to use the tools they are gifted at to drive business decisions, and allows stakeholders to self-serve on what the data team is building, instead of going through a backlog.

In addition to providing secure, authenticated report sharing, _Datapane Teams_ allows automated report generation by allowing data teams to deploy their Python scripts and Jupyter Notebooks to the cloud. Reports can be generated from parameters entered through web forms, on a schedule, or on-demand through our HTTP and Python APIs.

Other features include:

* APIs to utilise blobs and secrets in your scripts
* [Whitelabel embedding](datapane-teams/styling.md) of Datapane reports in your own products
* [Groups and secure-sharing features](datapane-teams/authentication-and-sharing/) to control access and share reports with external clients
* and [many more](https://datapane.com/enterprise/)


<div class="result" markdown>
<div class="grid cards" markdown>

-   :material-lightbulb-on-10:{ .lg .middle } __Concepts__

    ---

    [:octicons-arrow-right-24: Read explanations of Datapane-specific concepts](#)

-   :material-format-list-numbered:{ .lg .middle } __Tutorials__

    ---

    [:octicons-arrow-right-24: Learn how to use Datapane through short exercises](#)

-   :material-navigation-variant-outline:{ .lg .middle } __Guides__

    ---

    [:octicons-arrow-right-24: Follow how-to guides that solve real-world problems](#)

-   :material-view-list:{ .lg .middle } __Reference__

    ---

    [:octicons-arrow-right-24: View the technical descriptions of the API and how to operate it](#)

</div>
</div>