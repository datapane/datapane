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
## Introduction

Datapane is an SDK which makes it fast and simple to generate data reports, dashboards, and apps from Python.

Reports can be exported as standalone HTML documents (this guide itself is a Datapane report 😉), or hosted on our platform, where they can be shared via a link or embedded in your application.
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

## Hosting Reports

### Sign up for Datapane Cloud

In addition to saving documents locally, you can use [Datapane Cloud](https://datapane.com/product/cloud) to host and share your reports.

- Create private workspaces to share your reports securely
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

Now, just change `report.save` to `report.upload` in your code and your report will be pushed to Datapane Cloud: """
    ),
    dp.Code(
        """
# report.save(path="Hello_world.html")

report.upload(name="Hello world")"""
    ),
    dp.Text(
        """
This will generate a report URL which you can send to someone else or paste into another platform for embedding.

## Next Steps

- [Sign up for a Datapane Cloud account](https://datapane.com/accounts/signup/)
- [Read the documentation](https://docs.datapane.com)
- [Browse the API docs](https://datapane.github.io/datapane/)
- [Join the community on GitHub Discussions](https://github.com/datapane/datapane/discussions)"""
    ),
)

report.save(
    path="hello.html",
    open=True,
)

# You can also upload your report to a Datapane Server by logging in then running the following
# report.upload(name="hello")
