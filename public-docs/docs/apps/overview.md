Apps are full-stack web applications that run Python functions directly from your server or notebook. This makes them a great way to build interactive data applications for your users that dynamically update from your data or run analytics code on demand. Apps require a backend server, and can be served from your local machine or deployed and hosted on a server.

## Example

Below is a simple Datapane App that looks similar to the Reports we've already demonstrated, but contains a simple `filter_df` function that processes a loaded DataFrame (the `iris` dataset) and returns it as a Datapane DataTable.

The App itself is a collection of Datapane Blocks with the addition of a `dp.Form` block. This defines a form with an embedded Text input (`dp.TextBox`) called `name`. When the App is served, the Form is displayed to the user, and when submitted, runs the function `filter_df`. The result of this function (which is a DataTable block) is presented to the user.

In just a few lines we have built a simple data app that allows multiple users to interactively query a dataset and work with our Python-based data analysis.

```python
from vega_datasets import data
import datapane as dp

# a globally-accessible DataFrame
df = data.iris()

def filter_df(column: str):
    # Our dynamic function
    return dp.DataTable(df[column])

# We define the App similar to a Report
view = dp.View(
    dp.Form(
        on_submit=filter_df,
        controls=dp.Controls(column=dp.Choice(options=list(df.columns), label="Select column to filter"))
    )
)

# Start serving the app (by default on http://localhost:8000)
dp.serve_app(view)
```

<!-- TODO - embed this app... -->

## App Basics

Apps build upon Reports and add a few simple concepts to make them dynamic:

- [Compute Blocks](./blocks.md), such as [dp.Form][datapane.blocks.compute.Form] and [dp.Dynamic][datapane.blocks.compute.Dynamic] are added to your app alongside any static [Display](../blocks/display-blocks.ipynb) and [Layout](../blocks/layout-blocks.ipynb) blocks, and provide the interface into backend functions.
- [Parameters](./functions-controls.md), such as [dp.TextBox][datapane.blocks.parameters.TextBox] above, and more complex controls such as [dp.Range][datapane.blocks.parameters.Range], provide an interactive set of Controls to use in your Forms in order to allow your viewers to specify parameters.
- [Backend functions](./functions-controls.md), such as `filter_df` above, take these parameters, run any processing needed, and return Display and Layout blocks.

Most other data app frameworks work by running your app from top to bottom every time something changes.

Datapane works differently, and instead you write regular Python functions which return blocks (such as display or layout components) that are inserted into your app. This means you can use any normal Python development environment, and in particular Jupyter.
