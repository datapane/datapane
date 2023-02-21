"""datapane app"""
import os
from pathlib import Path

import folium
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from bokeh.plotting import figure
from matplotlib.collections import EventCollection

import datapane as dp
import datapane.blocks.asset
import datapane.blocks.text
from datapane.builtins import gen_df, gen_plot

lis = [1, 2, 3]

# Bokeh
p = figure(title="simple line example", x_axis_label="x", y_axis_label="y")
p.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], legend_label="Temp.", line_width=2)
bokeh_asset = datapane.blocks.asset.Plot(data=p)

# Folium
m = folium.Map(location=[45.372, -121.6972], zoom_start=12, tiles="Stamen Terrain")
folium.Marker(location=[45.3288, -121.6625], popup="Mt. Hood Meadows", icon=folium.Icon(icon="cloud")).add_to(m)
folium.Marker(location=[45.3311, -121.7113], popup="Timberline Lodge", icon=folium.Icon(color="green")).add_to(m)
folium.Marker(
    location=[45.3300, -121.6823], popup="Some Other Location", icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)
folium_asset = datapane.blocks.asset.Plot(data=m)

# Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(x=[0, 1, 2, 3, 4, 5], y=[1.5, 1, 1.3, 0.7, 0.8, 0.9]))
fig.add_trace(go.Bar(x=[0, 1, 2, 3, 4, 5], y=[1, 0.5, 0.7, -1.2, 0.3, 0.4]))
plotly_asset = datapane.blocks.asset.Plot(data=fig)

# Markdown
md_block = datapane.blocks.inline_text.Text(
    text=f"# Test markdown block with env var: {os.environ['ENV_VAR']} \n Test **content**"
)

# Downloadable file
file_asset = datapane.blocks.asset.Attachment(data=lis)

# In-line image
img_asset = datapane.blocks.asset.Media(file=Path("./datapane-icon-192x192.png"))

# Vega
vega_asset = datapane.blocks.asset.Plot(data=gen_plot())

# Table
df_table_asset = datapane.blocks.asset.Table(gen_df())
df_datatable_asset = datapane.blocks.asset.DataTable(gen_df(10000))

# Matplotlib
np.random.seed(19680801)
xdata = np.random.random([2, 10])
xdata1 = xdata[0, :]
xdata2 = xdata[1, :]
xdata1.sort()
xdata2.sort()
ydata1 = xdata1**2
ydata2 = 1 - xdata2**3
mpl_fig = plt.figure(figsize=(15, 15))
ax = mpl_fig.add_subplot(1, 1, 1)
ax.plot(xdata1, ydata1, color="tab:blue")
ax.plot(xdata2, ydata2, color="tab:orange")
xevents1 = EventCollection(xdata1, color="tab:blue", linelength=0.05)
xevents2 = EventCollection(xdata2, color="tab:orange", linelength=0.05)
yevents1 = EventCollection(ydata1, color="tab:blue", linelength=0.05, orientation="vertical")
yevents2 = EventCollection(ydata2, color="tab:orange", linelength=0.05, orientation="vertical")
ax.add_collection(xevents1)
ax.add_collection(xevents2)
ax.add_collection(yevents1)
ax.add_collection(yevents2)
ax.set_xlim([0, 1])
ax.set_ylim([0, 1])
ax.set_title("line plot with data points")
mpl_asset = datapane.blocks.asset.Plot(mpl_fig)

# Report
blocks = [
    df_table_asset,
    md_block,
    vega_asset,
    img_asset,
    file_asset,
    bokeh_asset,
    plotly_asset,
    folium_asset,
    mpl_asset,
]

dp.save_report(dp.App(blocks=blocks), path="local_xml_report.html")
# add datatable
blocks.append(df_datatable_asset)
dp.upload_report(dp.App(blocks=blocks), name="xml_report", overwrite=True)
