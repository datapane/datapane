"""test_proj1 script"""

__version__ = "0.1"

import pandas as pd

from datapane.client import api

# TODO - enter your code here...
df = pd.DataFrame.from_dict({"x": [4, 3, 2, 1], "y": [10.5, 20.5, 30.5, 40.5]})


"""Render and return your datapane report components"""
api.Report(
    # api.Markdown(f"Dummy Markdown block - {parameters.val}"),
    api.Markdown("Dummy Markdown block"),
    api.Asset.upload_df(df),
)
