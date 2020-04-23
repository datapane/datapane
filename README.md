![Datapane logo](https://datapane.com/static/datapane-logo-dark.png)

Datapane is a Python library which makes it simple to build reports from the common objects in your data analysis, such as pandas DataFrames, plots from Python visualisation libraries, and Markdown. 

Reports can be exported as standalone HTML documents, with rich components which allow data can explored and visualisations can be used interactively.

For example, create a report with a table viewer and an interactive plot:

```python
import altair as alt
import pandas as pd
from datapane import LocalReport, Table, Plot
​
df = pd.read_csv('https://query1.finance.yahoo.com/v7/finance/download/GOOG?period1=1553600505&period2=1585222905&interval=1d&events=history')
chart = alt.Chart(df).encode(x='Date', y='High', y2='Low').mark_area(opacity=0.5).interactive()
​
LocalReport.create([
    Table.create(df), 
    Plot.create(chart)
])
```

Would create a report such as this...

![Report Example](https://gblobscdn.gitbook.com/assets%2F-LnsT7A86qlOk1jk5wSj%2F-M3C-gLdrhOWo65CIbWB%2F-M3C0REll7dsea0Pw51q%2Fimage.png)

With an interactive Table and Plot component.

# Getting Started
