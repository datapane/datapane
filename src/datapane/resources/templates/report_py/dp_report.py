# Sample Datapane Report - {{ name }}

import pandas as pd
import altair as alt
import datapane as dp

# download data & group by manufacturer
df = pd.read_csv('https://covid.ourworldindata.org/data/vaccinations/vaccinations-by-manufacturer.csv', parse_dates=['date'])
df = df.groupby(['vaccine', 'date'])['total_vaccinations'].sum().tail(1000).reset_index()

# plot vaccinations over time using Altair
plot = alt.Chart(df).mark_area(opacity=0.4, stroke='black').encode(
    x='date:T',
    y=alt.Y('total_vaccinations:Q'),
    color=alt.Color('vaccine:N', scale=alt.Scale(scheme='set1')),
    tooltip='vaccine:N'
).interactive().properties(width='container')

# tablulate total vaccinations by manufacturer
total_df = df[df["date"] == df["date"].max()].sort_values("total_vaccinations", ascending=False).reset_index(drop=True)
total_styled = total_df.style.bar(subset=["total_vaccinations"], color='#5fba7d', vmax=total_df["total_vaccinations"].sum())

# embed into a Datapane Report
report = dp.Report(
    "## Vaccination Report",
    dp.Plot(plot, caption="Vaccinations by manufacturer over time"),
    dp.Table(total_styled, caption="Current vaccination totals by manufacturer"),
    dp.Table(df, caption="Initial Dataset")
)
report.publish(name='Covid Vaccinations Demo {{ name }}',
               description="Covid Vaccinations report, using data from ourworldindata", open=True)
