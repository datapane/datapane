import unittest
from datetime import timedelta

import numpy as np
import pandas as pd

from datapane.common.df_processor import to_df


def assert_unnamed_col_works(col):
    out_df = to_df(col)
    assert out_df.columns == ["Result"]
    assert len(out_df) == len(col)


def assert_named_col_works(col):
    out_df = to_df(col)
    assert out_df.columns.tolist() == [col.name]
    assert len(out_df) == len(col)


def assert_scalar_works(scalar):
    out_df = to_df(scalar)
    assert out_df.columns == ["Result"]
    assert len(out_df) == 1
    assert out_df.iloc[0, 0] == scalar


def test_to_df_df():
    empty = pd.DataFrame()
    new_df = to_df(empty)
    pd.testing.assert_frame_equal(empty, new_df, check_like=True)


def test_to_df_series():
    assert_unnamed_col_works(pd.Series([2, 3, 5]))


def test_to_df_index():
    assert_unnamed_col_works(pd.Index([2, 3, 5]))


def test_to_df_series_named():
    assert_named_col_works(pd.Series([2, 3, 5], name="test"))


def test_to_df_index_named():
    assert_named_col_works(pd.Index([2, 3, 5], name="test"))


def test_to_df_int():
    assert_scalar_works(3)


def test_to_df_float():
    assert_scalar_works(0.3)


def test_to_df_bool():
    assert_scalar_works(True)


def test_to_df_str():
    assert_scalar_works("test")


def test_to_df_numpy_scaler():
    assert_scalar_works(np.int64(5))


def test_to_df_numpy_bool():
    assert_scalar_works(bool(True))


def test_to_df_datetime():
    now = pd.to_datetime("now")
    assert_scalar_works(now)


def test_to_df_datetime_timezoned():
    now = pd.to_datetime("now", utc=True)
    assert_scalar_works(now)


def test_to_df_timedelta():
    delta = pd.to_timedelta(timedelta(days=1, seconds=10000, microseconds=100000))
    assert_scalar_works(delta)


def test_to_df_2_dim_numpy_array():
    out_df = to_df(np.array([[2, 3], [4, 5]]))
    unittest.TestCase().assertListEqual(out_df.columns.tolist(), [0, 1])
    assert out_df.shape == (2, 2)


def test_to_df_numpy_array_redundant_dims():
    out_df = to_df(np.array([[[2, 3]]]))
    assert out_df.columns == ["Result"]
    assert out_df.shape == (2, 1)


def test_to_df_numpy_array_redundant_dims_scaler():
    out_df = to_df(np.array([[[3]]]))
    assert out_df.columns == ["Result"]
    assert out_df.iloc[0, 0] == 3


def test_to_df_structured_array():
    out_df = to_df(
        np.array(
            [("Rex", 9, 81.0), ("Fido", 3, 27.0)],
            dtype=[("name", "U10"), ("age", "i4"), ("weight", "f4")],
        )
    )
    unittest.TestCase().assertListEqual(out_df.columns.tolist(), ["name", "age", "weight"])
