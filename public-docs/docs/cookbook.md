Find some recipes for useful things you can build using Datapane!

## Iris dimension visualization

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
view = dp.View(
    "# Iris Dataset Plotter",
    dp.Form(plot, submit_label="Plot", controls=controls),
)
dp.serve_app(view)
```

<!-- We've deployed the app to Fly.io using our [deployment docs](/deployment/deployed_apps/). You can view it here:

## TODO
 - iframe to app on fly.io (served using `embed_mode=True`) -->


## Data exploration via DuckDB

[DuckDB](https://duckdb.org/) provides a great way to do fast analytics in SQL. Combine it with Datapane to build an app to query a database using forms. The following app allows you to explore the airports in the USA, and plots the results on a map.

```python
import datapane as dp
import pandas as pd
import altair as alt
import duckdb
import altair as alt
from vega_datasets import data

alt.data_transformers.disable_max_rows()
states = alt.topo_feature(data.us_10m.url, feature='states')

background = alt.Chart(states).mark_geoshape(
    fill='#f1f5f9',
    stroke='#818cf8',
).project('albersUsa').properties(height=600, width='container')

df = data.airports()

con = duckdb.connect()

con.execute("CREATE TABLE my_table AS SELECT * FROM df")
con.execute("INSERT INTO my_table SELECT * FROM df")

def get_sample(params):
    display_name = params['state']
    sample = con.execute(f"SELECT * FROM my_table WHERE state = '{display_name}'").df()

    points = alt.Chart(sample).mark_circle(color="#4f46e5").encode(
        longitude='longitude:Q',
        latitude='latitude:Q',
        size=alt.value(10),
        tooltip='name'
    ).project(
        "albersUsa",
    )
    return [background + points, dp.DataTable(sample)]

v = dp.View(
  dp.Text("# Airport searcher"),
  dp.Form(
      on_submit=get_sample,
      controls=[
          dp.Choice(
              options=list(df['state'].dropna().unique()),
              name='state',
          )
      ],
  )
)

dp.serve_app(v)
```

## Processing an uploaded image

This example demonstrates how to create an app with Datapane. The app allows the user to upload an image, which is then processed to remove its background. The original and processed images are then displayed to the user, along with a download link for each.

```python
import datapane as dp
from rembg import remove
from PIL import Image


def process_image(params):
    image = Image.open(params["upload"])
    fixed = remove(image)
    image.save("original.png", "PNG")
    fixed.save("processed.png", "PNG")

    return dp.Group(
        dp.Group(
            "## Original Image 📷",
            dp.Media(file="original.png"),
            dp.Attachment(file="original.png"),
        ),
        dp.Group(
            "## Processed Image 🔧",
            dp.Media(file="processed.png"),
            dp.Attachment(file="processed.png"),
        ),
        columns=2,
    )


v = dp.View(
    "# Background Remover 🪄",
    dp.Form(
        process_image,
        label="Upload and Process Image",
        controls=[dp.File("upload", label="Original Image")],
    ),
)

dp.serve_app(v)
```
