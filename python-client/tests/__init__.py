import pandas as pd


def check_df_equal(left: pd.DataFrame, right: pd.DataFrame, **kwargs):
    """
    Wraps pd.assert_frame_equal whilst processing dfs and ignoring the order of the columns.
    NOTE - this mutates the dfs
    """
    from datapane.common.df_processor import process_df

    left = process_df(left)
    right = process_df(right)
    pd.testing.assert_frame_equal(left, right, check_like=True, **kwargs)
