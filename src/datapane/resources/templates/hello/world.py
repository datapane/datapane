# Based on the example from hello.py
import altair as alt
import datapane as dp
from vega_datasets import data

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

report = dp.Report(
    """🎆 Congratulations on uploading your first Datapane report!! 🎆""",
    dp.Formula("x^2 + y^2 = z^2"),
    dp.Group(
        dp.BigNumber(heading="Number of percentage points", value="84%", change="2%", is_upward_change=True),
        dp.BigNumber(heading="Simple Statistic", value=100),
        columns=2,
    ),
    dp.Select(dp.Plot(plot1, label="Chart"), dp.DataTable(source, label="Data")),
)

report.upload(name="Hello World", description="My first Datapane Report", tags=["example"], open=True)
