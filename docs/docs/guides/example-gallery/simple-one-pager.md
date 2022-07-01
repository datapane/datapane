# Simple one-pager

If you only have a single dataframe and a couple of charts, you can wrap them inside a Datapane report as follows:&#x20;

```python
import datapane as dp
import altair as alt
from vega_datasets import data

source = data.cars()

plot1 = alt.Chart(source).mark_circle(size=60).encode(
  x='Horsepower',
  y='Miles_per_Gallon',
  color='Origin',
  tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
).interactive()


report = dp.Report(
    dp.Text("## Simple Datapane Report with plot and table"),
    dp.Plot(plot1),
    dp.DataTable(source)
)

report.upload(name="Hello world")
```

Running that code generates the following report:&#x20;

{% embed url="https://datapane.com/u/johnmicahreid/reports/0kzZz2k/hello-world/embed" %}
