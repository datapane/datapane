"""test_proj1 app"""
import pandas as pd

import datapane.blocks.text
from datapane.client import api

# TODO - enter your code here...
df = pd.DataFrame.from_dict({"x": [4, 3, 2, 1], "y": [10.5, 20.5, 30.5, 40.5]})


def render():
    """Render and return your datapane report components"""
    return [
        # api.Markdown("Dummy Markdown block - {parameters.val}"),
        datapane.blocks.inline_text.Text("Dummy Markdown block"),
        api.Asset.upload_df(df),
    ]
