# Dashboard with rows and columns

The [Group](../../reports/blocks/layout-pages-and-selects.md#grid-layouts) block is a great way to create grid layouts - just specify the number of rows and columns you want. You can also nest groups within each other. If you have a non-fixed number of plots, you can pass them in as a list via the `blocks` parameter:&#x20;

```python
import altair as alt
from vega_datasets import data
import datapane as dp

source = data.cars()

origins = source.Origin.unique()
plots = []

# Create a list of plots
for o in origins: 
    plot = alt.Chart(source[source.Origin == o]).mark_circle(size=60).encode(
      x='Horsepower',
      y='Miles_per_Gallon',
      tooltip=['Name', 'Horsepower', 'Miles_per_Gallon']
    ).properties(title=o
    ).interactive()
    
    plots.append(plot)

report = dp.Report(
  dp.Group(
      dp.Text("![](https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=1470&q=80)"),
      dp.Group(
          dp.BigNumber(
              heading="Total datapoints",
              value=source.Name.count(),
          ), 
          dp.BigNumber(
              heading="Average miles per gallon",
              value=round(source.Miles_per_Gallon.mean(), 2)
          ),
          rows=2
      ), columns = 2
  ),
  dp.Group(
      blocks = plots,
      columns = len(plots),
  )
)

report.upload(name="Dashboard layout")
```

Running this code generates the following report:&#x20;

{% embed url="https://datapane.com/u/johnmicahreid/reports/9AxpJQA/dashboard-layout/embed" %}
