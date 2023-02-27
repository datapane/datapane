# An example app

This example demonstrates an app that allows the user to visualise different dimensions of the Iris flower dataset.


```python
import altair as alt
import datapane as dp
from vega_datasets import data

dataset = data.iris()
columns = list(dataset.columns)


def plot(params):
    global dataset

    fig = (
        alt.Chart(dataset)
        .mark_point()
        .encode(
            x=alt.X(params["x_axis"], scale=alt.Scale(zero=False)),
            y=alt.X(params["y_axis"], scale=alt.Scale(zero=False)),
            color=params["color"],
            tooltip=columns,
        )
    )

    return dp.Plot(fig, name="plot")


plot({"x_axis": "sepalLength", "y_axis": "sepalWidth", "color": "species"})

controls = dp.Controls(
    dp.Choice("x_axis", options=columns),
    dp.Choice("y_axis", options=columns),
    dp.Choice("color", options=columns),
)

v = dp.Blocks(
    "# Iris Dataset Plotter",
    dp.Form(plot, submit_label="Plot", controls=controls),
)

dp.serve_app(v)
```

<!-- We've deployed the app to Fly.io using our [deployment docs](/deployment/deployed_apps/). You can view it here:

## TODO
 - iframe to app on fly.io (served using `embed_mode=True`) -->
