# Based on the example from hello.py
import altair as alt
from vega_datasets import data

import datapane as dp
import datapane.blocks.asset
import datapane.blocks.layout
import datapane.blocks.text

source = data.cars()

plot1 = (
    alt.Chart(source)
    .mark_circle(size=60)
    .encode(
        x="Horsepower",
        y="Miles_per_Gallon",
        color="Origin",
        tooltip=["Name", "Origin", "Horsepower", "Miles_per_Gallon"],
    )
    .interactive()
)

report = dp.App(
    """🎆 Congratulations on uploading your first Datapane report!! 🎆""",
    datapane.blocks.inline_text.Formula("x^2 + y^2 = z^2"),
    datapane.blocks.layout.Group(
        dp.BigNumber(heading="Number of percentage points", value="84%", change="2%", is_upward_change=True),
        dp.BigNumber(heading="Simple Statistic", value=100),
        columns=2,
    ),
    datapane.blocks.layout.Select(
        datapane.blocks.asset.Plot(plot1, label="Chart"), datapane.blocks.asset.DataTable(source, label="Data")
    ),
)

report.upload(name="Hello World", description="My first Datapane Report", tags=["example"], open=True)
