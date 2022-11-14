import os

import pandas as pd

import datapane as dp
import datapane.blocks.asset
import datapane.blocks.text

# basic report creation, with params and env vars
df = pd.DataFrame.from_dict({"x": [4, 3, 2, 1], "y": [10.5, 20.5, 30.5, 40.5]})
blocks = [datapane.blocks.inline_text.Text(f"Dummy Markdown block - {dp.Params['p1']}"), datapane.blocks.asset.DataTable(df), datapane.blocks.inline_text.Text(f"Text block with env var: {os.environ['ENV_VAR']}")]

# test running as main or by datapane runner
if dp.ON_DATAPANE:
    print("on datapane")
if __name__ == "__datapane__":  # same as dp.by_datapane
    print("by datapane")
    report = dp.App(blocks=blocks)
    report.upload(name="dp_report", description="Description", overwrite=True)
