# Multiple pages

Datapane allows you to add multiple [pages](../../reports/blocks/layout-pages-and-selects.md#pages) to a report as follows:&#x20;

```python
import altair as alt
from vega_datasets import data
import datapane as dp

source = data.cars()

plot = alt.Chart(source).mark_circle(size=60).encode(
  x='Horsepower',
  y='Miles_per_Gallon',
  tooltip=['Name', 'Horsepower', 'Miles_per_Gallon']
).interactive()

report = dp.Report(
    dp.Page(
        dp.Text("This report explains how to add multiple pages. ![](https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=1470&q=80)"),
        title = "Introduction"),
    dp.Page(
        dp.Plot(plot),
        title = "Chart"
    ), 
    dp.Page(
        dp.DataTable(source),
        title = "Data"
   )
)

report.upload(name="Multi-page report")
```

Running that code generates the following report:&#x20;

{% embed url="https://datapane.com/u/johnmicahreid/reports/E7ylOD3/multi-page-report/embed" %}
