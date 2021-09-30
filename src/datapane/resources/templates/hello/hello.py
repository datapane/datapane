import altair as alt
from vega_datasets import data

import datapane as dp

source = data.cars()

plot1 = (
    alt.Chart(source)
    .mark_circle(size=60)
    .encode(
        x="Horsepower",
        y="Miles_per_Gallon",
        color="Origin",
        tooltip=["Name", "Origin", "Horsepower", "Miles_per_Gallon"],
    )
    .interactive()
)

report = dp.Report(
    dp.Text(
        """
![Imgur](https://i.imgur.com/S3MGxWd.png)
## Introduction

Datapane is a Python library for building interactive reports from data components like pandas DataFrames, Altair/ Plotly/Matplotlib charts, and Markdown.

Reports can be exported as standalone HTML documents (this guide itself is a Datapane report 😉), or hosted on our platform, where they can be shared via a link or embedded in your application.
## Explainer Video
"""
    ),
    dp.HTML(
        """
<script src="https://fast.wistia.com/embed/medias/xekc17kmgs.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><div class="wistia_responsive_padding" style="padding:62.5% 0 0 0;position:relative;"><div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%;"><div class="wistia_embed wistia_async_xekc17kmgs videoFoam=true" style="height:100%;position:relative;width:100%"><div class="wistia_swatch" style="height:100%;left:0;opacity:0;overflow:hidden;position:absolute;top:0;transition:opacity 200ms;width:100%;"><img src="https://fast.wistia.com/embed/medias/xekc17kmgs/swatch" style="filter:blur(5px);height:100%;object-fit:contain;width:100%;" alt="" aria-hidden="true" onload="this.parentNode.style.opacity=1;" /></div></div></div></div>
    """
    ),
    dp.Text(
        """
## Hello world

Let's start with a minimal example to understand the basic flow (feel free to copy-paste this code and follow along in your IDE or notebook).  Imagine you have an existing notebook where you've analysed and charted some data:
"""
    ),
    dp.Code(
        """
import altair as alt
from vega_datasets import data

source = data.cars()

plot1 = alt.Chart(source).mark_circle(size=60).encode(
  x='Horsepower',
  y='Miles_per_Gallon',
  color='Origin',
  tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
).interactive()"""
    ),
    dp.Text(
        """
To share this with someone non-technical, you'd typically send them a raw notebook file or put screenshots in a presentation. Instead, let's build an interactive report using Datapane - just add the following lines:
"""
    ),
    dp.Code(
        """
import datapane as dp

report = dp.Report(
    dp.Plot(plot1),
    dp.DataTable(source)
)

report.save(path="Hello_world.html")"""
    ),
    dp.Text(
        """
After we import the library, we create a report object, wrap our chart in a Plot block, dataframe in a DataTable block, then save as a standalone HTML document. Now users can open this report in their browser and interact with these objects:
"""
    ),
    dp.Plot(plot1),
    dp.DataTable(source),
    dp.Text(
        """
## A more complex example

Datapane also has a lot of pre-built components for layout and interactivity, which can help you present more complex data. Let's explore some of these:
"""
    ),
    dp.Code(
        """
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

report = dp.Report(
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
      ), columns=2
  ),
  dp.Select(
      dp.Plot(plot1, label="Chart"),
      dp.DataTable(source, label="Data")
  ),
)

report.save(path="Layout_example.html")"""
    ),
    dp.Text(
        """
The syntax is pretty similar, except Select and Group blocks allow you to nest other blocks inside. This is helpful when you need a non-linear or dashboard layout.

Running that code generates the following report: """
    ),
    dp.Formula("x^2 + y^2 = z^2"),
    dp.Group(
        dp.BigNumber(heading="Number of percentage points", value="84%", change="2%", is_upward_change=True),
        dp.BigNumber(heading="Simple Statistic", value=100),
        columns=2,
    ),
    dp.Select(
        dp.Plot(plot1, label="Chart"),
        dp.DataTable(source, label="Data"),
    ),
    dp.Text(
        """
These are great ways to add interactivity to your report with minimal effort. Spice things up even further by adding pages, HTML blocks, images and more.

## Sharing Reports

### Sign up for Datapane Studio

In addition to saving documents locally, you can use [Datapane Studio](https://datapane.com/explore) to host and share your reports.

- Unlimited public reports, plus limited private reports
- Embed reports in places like Medium, Notion, or your own website (see [here](https://docs.datapane.com/reports/embedding-reports-in-social-platforms))
- Viewers can explore and download your data with additional DataTable analysis features

To get your free API key, run the following command:
"""
    ),
    dp.Select(
        dp.Code("$ datapane signup", label="Terminal"),
        dp.Code("!datapane signup", label="Python/Jupyter"),
    ),
    dp.Text(
        """
Once you've completed signup, your API key will be stored in your environment (you can also see it in your [profile](https://datapane.com/settings/).

Now, just change `report.save` to `report.upload` in your code and your report will be pushed to Datapane.com: """
    ),
    dp.Code(
        """
# report.save(path="Hello_world.html")

report.upload(name="Hello world")"""
    ),
    dp.Text(
        """
This will generate a report URL which you can send to someone else or paste into another platform for embedding.

### Datapane Teams

[Datapane Teams](https://docs.datapane.com/datapane-teams/) is our plan for organizations, which adds the following features on top of Studio: 

- Share unlimited reports privately with your company or external clients
- Manage users, groups and permissions
- Deploy Jupyter Notebooks and scripts as apps, with inputs that can be run by your team interactively to dynamically create results
- Schedule reports to automatically update

Datapane Teams is offered as both a managed SaaS service and an on-prem install. For more information, see [the documentation](https://docs.datapane.com/datapane-teams/tut-deploying-a-script). You can find pricing [here](https://datapane.com/pricing).

## Next Steps

- [Sign up for a Datapane Studio account](https://datapane.com/accounts/signup/)
- [Read the documentation](https://docs.datapane.com)
- [Browse the API docs](https://datapane.github.io/datapane/)
- [Browse samples and demos](https://github.com/datapane/gallery/)
- [Join the community on GitHub Discussions](https://github.com/datapane/datapane/discussions)"""
    ),
)

report.save(
    path="hello.html",
    formatting=dp.ReportFormatting(width=dp.ReportWidth.NARROW),
    open=True,
)

# You can also upload your report to a Datapane Server by logging in then running the following
# report.upload(name="hello")
