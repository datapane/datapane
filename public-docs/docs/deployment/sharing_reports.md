Reports provide a fast and easy way to share insights. Reports do not allow compute blocks, which means they can be exported as a standalone file which can be shared without a server. All data and plots are encapsulated in a single HTML file, which provides a secure and low-barrier sharing method.

Compatible blocks can be exported as a standalone report using `dp.save_report`:

```python

import datapane as dp
from vega_datasets import data

df = data.iris()

v = dp.Blocks(dp.DataTable(df))

dp.save_report(v, path='report.html')
```
