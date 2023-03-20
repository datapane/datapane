This example demonstrates an app that allows the user to visualize different dimensions of the Iris flower dataset.

```python
import random
import altair as alt
import datapane as dp
from vega_datasets import data

# load the dataset as a global value
dataset = data.iris()
columns = list(dataset.columns)

def plot(x_axis: str, y_axis: str, color: str) -> dp.Plot:
    """Create and return the plot"""
    fig = (
        alt.Chart(dataset)
        .mark_point()
        .encode(
            x=alt.X(x_axis, scale=alt.Scale(zero=False)),
            y=alt.X(y_axis, scale=alt.Scale(zero=False)),
            color=color,
            tooltip=columns,
        )
    )

    return dp.Plot(fig)

# App setup
controls = dp.Controls(
    dp.Choice("x_axis", options=columns, initial=random.choice(columns)),
    dp.Choice("y_axis", options=columns, initial=random.choice(columns)),
    dp.Choice("color", options=columns, initial=random.choice(columns)),
)
blocks = dp.Blocks(
    "# Iris Dataset Plotter",
    dp.Form(plot, submit_label="Plot", controls=controls),
)
dp.serve_app(blocks)
```

<!-- We've deployed the app to Fly.io using our [deployment docs](/deployment/deployed_apps/). You can view it here:

## TODO
 - iframe to app on fly.io (served using `embed_mode=True`) -->
