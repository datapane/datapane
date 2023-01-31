import altair as alt
from vega_datasets import data

import datapane as dp

df = data.iris()
fig = alt.Chart(df).mark_point().encode(x="petalLength:Q", y="petalWidth:Q", color="species:N")


report = dp.App(
    dp.Text(
        """
# Hello world

Welcome to [Datapane](https://datapane.com)! Built for data developers, Datapane makes it simple to create beautiful reports from anywhere we can run Python.

Reports can be exported as standalone HTML documents or hosted on Datapane Cloud, where they can be shared via a link or embedded.

This [_Hello world_](https://github.com/datapane/datapane/blob/master/src/datapane/resources/templates/hello/hello.py) page itself was generated with Datapane!
        """
    ),
    dp.Text(
        """
## Our first Report

Let’s create a simple report! In this scenario, we have a dataset and visualization that we need to share with our colleagues.
        """
    ),
    dp.Code(
        """
import altair as alt
from vega_datasets import data

df = data.iris()
fig = (
    alt.Chart(df)
    .mark_point()
    .encode(x="petalLength:Q", y="petalWidth:Q", color="species:N")
)
        """
    ),
    dp.Text(
        """
        Datapane makes generating a report simple – all it takes is the following.
        """
    ),
    dp.Code(
        """
import datapane as dp

report = dp.App(
    dp.Plot(fig),
    dp.DataTable(df)
)

report.save(path="my_report.html")
        """
    ),
    dp.Text(
        """
This will generate an HTML file, `my_report.html`, containing our interactive report:
        """
    ),
    dp.Plot(fig),
    dp.DataTable(df),
    dp.Text(
        """
We can now open our standalone HTML report with a web browser and email it to our colleagues who can do the same. 

But what if we want to send a link to our report or embed it instead?

## Datapane Cloud makes it simple to share

Datapane Cloud is free! Share reports privately, or embed them into platforms like Salesforce and Medium.

To sign up go to https://cloud.datapane.com/accounts/signup/ and then login by doing the following
"""
    ),
    dp.Select(
        dp.Code("$ datapane login", label="Terminal"),
        dp.Code("!datapane login", label="Python/Jupyter"),
    ),
    dp.Text(
        """
Once we've logged in, [the API key](https://datapane.com/settings/) will be stored in the current environment.
        """
    ),
    dp.Code(
        """
report.upload(name="My report")
        """
    ),
    dp.Text(
        """
By using `upload()` in place of `save()`, our report is uploaded to Datapane Cloud and a shareable link is generated. 

We can now send this link to our colleagues or use it to embed our report on another platform.

## Next steps

There's so much more we can do with Datapane!
- [Read the documentation](https://docs.datapane.com)
- [Explore our community spaces](https://datapane.com/community)
- [We're open-source – browse the Datapane repo](https://github.com/datapane/datapane)
- [Sign up for a Datapane Cloud account](https://cloud.datapane.com/accounts/signup/)
"""
    ),
)

report.save(
    path="hello.html",
    open=True,
)

# You can also upload your report to a Datapane Server by logging in then running the following
# report.upload(name="hello-world", open=True)
