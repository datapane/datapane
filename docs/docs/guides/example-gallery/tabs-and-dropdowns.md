# Tabs and Dropdowns

If you have multiple pieces of content that you don't want to show at the same time, consider using the [Select](../../reports/blocks/layout-pages-and-selects.md#tabs-and-selects) block. These can be nested inside each other, and can show Tabs (5 or less options) or Dropdowns:&#x20;

```python
import altair as alt
from vega_datasets import data
import datapane as dp
import numpy as np

source = data.cars()

cylinders = np.sort(source.Cylinders.unique())
plots = []

# Create a list of plots
for c in cylinders: 
    plot = alt.Chart(source[source.Cylinders == c]).mark_circle(size=60).encode(
      x='Horsepower',
      y='Miles_per_Gallon',
      tooltip=['Name', 'Horsepower', 'Miles_per_Gallon']
    ).properties(title = c.astype(str) + " Cylinders"
    ).interactive()
    
    plots.append(plot)

report = dp.Report(
    dp.Select(blocks = [
        dp.Select(
            blocks=[dp.Plot(p, label=(c.astype(str) + " Cylinders")) for p, c in zip(plots, cylinders)], 
            label = "Dropdown"),
        dp.Select(
            blocks=[dp.Plot(p, label=(c.astype(str) + " Cylinders")) for p, c in zip(plots, cylinders)], 
            label = "Tabs",
            type=dp.SelectType.TABS # Override default choice
        ),
    ])
)

report.upload(name="Tabs and Dropdowns")
```

Running that code generates the following result:&#x20;

{% embed url="https://datapane.com/u/johnmicahreid/reports/9ArDJZ7/tabs-and-dropdowns/embed" %}
