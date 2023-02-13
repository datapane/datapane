"""My cool plot"""
import altair as alt
import pandas as pd

import datapane.blocks.asset

df = pd.read_csv(
    "https://query1.finance.yahoo.com/v7/finance/download/GOOG?period2=1585222905&interval=1mo&events=history"
)

chart = (
    alt.Chart(df)
    .encode(
        x="Date:T",
        y="Open",
        y2="Close",
        color=alt.condition("datum.Open <= datum.Close", alt.value("#06982d"), alt.value("#ae1325")),
    )
    .mark_bar()
    .interactive()
)


report = [datapane.blocks.asset.Plot(chart)]
