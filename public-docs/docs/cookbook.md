## Introduction

Find some recipes for useful things you can build using Datapane!

## Using DuckDB and Altair to build a data exploration tool

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

v = dp.Blocks(
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

## Using image processing libraries to process an uploaded image

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


v = dp.Blocks(
    "# Background Remover 🪄",
    dp.Form(
        process_image,
        label="Upload and Process Image",
        controls=[dp.File("upload", label="Original Image")],
    ),
)

dp.serve_app(v, embed_mode=True)
```
