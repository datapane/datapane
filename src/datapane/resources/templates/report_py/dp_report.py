"""{{ name }} report"""
import altair as alt
import pandas as pd
import datapane as dp

# get the data
dataset = pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv")
df = dataset.groupby(["continent", "date"])["new_cases_smoothed_per_million"].mean().reset_index()

# build an altair plot
plot = alt.Chart(df).mark_area(opacity=0.4, stroke='black').encode(
    x='date:T',
    y=alt.Y('new_cases_smoothed_per_million:Q', stack=None),
    color=alt.Color('continent:N', scale=alt.Scale(scheme='set1')),
    tooltip='continent:N'
).interactive().properties(width='container')

# embed data and plot into a Datapane report and publish
report = dp.Report("## Covid data per continent", dp.Plot(plot), dp.DataTable(df))
report.publish(
    name="Covid Demo {{ name }}",
    description="Plot of Covid infections per continent, using data from ourworldindata",
    open=True,
)
