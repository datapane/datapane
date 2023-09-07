import sys
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import mktemp

import numpy as np
import pandas as pd
import vega_datasets as vd

from datapane.common import ArrowFormat, SList, log
from datapane.common.df_processor import (
    PD_VERSION,
    convert_axis,
    downcast_numbers,
    obj_to_str,
    parse_categories,
    process_df,
    timedelta_to_str,
)


def _check_categories_parsed(df: pd.DataFrame, categorical_columns: SList):
    assert set(list(df.select_dtypes("category").columns)) == set(categorical_columns)


def _check_is_object(df: pd.DataFrame, object_columns: SList):
    assert set(list(df.select_dtypes("object").columns)) == set(object_columns)


def _check_is_string(df: pd.DataFrame, object_columns: SList):
    assert set(list(df.select_dtypes("string").columns)) == set(object_columns)


def save_load_arrow(tmp_path: Path, df: pd.DataFrame) -> pd.DataFrame:
    """Roundtrip via an arrow file"""
    fn = mktemp(".arrow", dir=tmp_path)
    ArrowFormat.save_file(str(fn), df.copy(deep=True))
    return ArrowFormat.load_file(fn)


def test_convert_axis():
    def _test_df(df: pd.DataFrame):
        convert_axis(df)
        assert df.columns.nlevels == 1
        assert df.index.nlevels == 1
        assert isinstance(df.index, pd.RangeIndex)

    # ontario systems df - as per https://github.com/datapane/datapane-hosted/issues/762
    data = {
        "Jan": pd.DataFrame(columns=["Market", "Units Sold", "New Customers"], data=[["East", 14, 1]]).set_index(
            "Market"
        ),
        "Feb": pd.DataFrame(columns=["Market", "Units Sold", "New Customers"], data=[["East", 45, 6]]).set_index(
            "Market"
        ),
    }
    df_o = pd.concat(data, axis=1)
    _test_df(df_o)

    # pandas multiindex demo
    index = pd.MultiIndex.from_tuples(
        [("bird", "falcon"), ("bird", "parrot"), ("mammal", "lion"), ("mammal", "monkey")], names=["class", "name"]
    )
    columns = pd.MultiIndex.from_tuples([("speed", "max"), ("species", "type")])
    df_m = pd.DataFrame([(389.0, "fly"), (24.0, "fly"), (80.5, "run"), (np.nan, "jump")], index=index, columns=columns)
    _test_df(df_m)


def test_parse_categories_small():
    data = pd.DataFrame(
        dict(
            str1=[str(x) for x in range(30)],
            str2=["a" for x in range(30)],
        )
    )
    parse_categories(data)
    _check_categories_parsed(data, ["str2"])


def test_parse_categories_large():
    data = pd.DataFrame(
        dict(
            str1=[str(x) for x in range(1000)],
            str2=[str(x % 25) for x in range(1000)],
        )
    )
    parse_categories(data)
    _check_categories_parsed(data, ["str2"])


def test_parse_categories_roundtrip(tmp_path: Path):
    # initial df
    df = pd.DataFrame(
        dict(
            str1=[str(x) for x in range(10000)],
            str2=[str(x % 25) for x in range(10000)],
        )
    )
    # process it
    df1 = process_df(df, copy=True)
    # arrow converted
    df2 = save_load_arrow(tmp_path, df)

    _check_categories_parsed(df2, ["str2"])
    pd.testing.assert_frame_equal(df1, df2)


def test_downcast_numbers():
    # ints
    data = pd.DataFrame(
        [[1, 1, 1, 1, 1, 1, 1, 1], [100, 1000, int(1e6), int(1e12), -100, -1000, int(-1e6), int(-1e12)]],
        columns=["num1_col", "num2_col", "num3_col", "num4_col", "num5_col", "num6_col", "num7_col", "num8_col"],
    )
    downcast_numbers(data)
    assert [str(x) for x in data.dtypes] == ["uint8", "uint16", "uint32", "uint64", "int8", "int16", "int32", "int64"]

    # floats - currently disabled
    # data = pd.DataFrame(
    #     [[1.0, 1.0, 1.0, 1.0, 1.0], [1e3, 1e6, 1e12, 1e30, 1e100]],
    #     columns=["num1_col", "num2_col", "num3_col", "num4_col", "num5_col"],
    # )
    # downcast_numbers(data)
    # assert [str(x) for x in data.dtypes] == ["float32", "float32", "float32", "float32", "float64"]


def test_timedelta_to_str():
    df = pd.DataFrame(
        dict(
            str_col=[str(x) for x in range(30)],
            int_col=[x for x in range(30)],
            time_col=[timedelta(seconds=x) for x in range(30)],
        )
    )
    timedelta_to_str(df)
    assert [str(x) for x in df.dtypes] == ["object", "int64", "object"]
    df1 = df.convert_dtypes()
    assert [str(x) for x in df1.dtypes] == ["string", "Int64", "string"]


def test_to_str():
    data = pd.DataFrame(
        dict(
            int_col=[x for x in range(32)],
            obj_col=[(str(x), str(x)) for x in range(30)] + [pd.NA, pd.NA],
            cat_obj_col=[("a", "b") for x in range(30)] + [pd.NA, pd.NA],
        )
    )

    data1 = data.copy(deep=True)
    obj_to_str(data1)
    _check_is_string(data1, ["obj_col", "cat_obj_col"])

    data2 = data.copy(deep=True)
    parse_categories(data2)
    obj_to_str(data2)
    _check_is_string(data2, ["obj_col"])
    assert type(data2["cat_obj_col"].cat.categories[0]) == str


def test_col_order(tmp_path: Path):
    def _test_order(df: pd.DataFrame):
        # process and compare
        df1 = process_df(df, copy=True)
        assert list(df.columns) == list(df1.columns)

        # convert to arrow and back
        df2 = save_load_arrow(tmp_path, df)
        assert list(df.columns) == list(df2.columns)

    data = pd.DataFrame(
        {
            "first_col": [1, 2, 3],
            "2nd_col": [1, 2, 3],
            "third_col_3": [1, 2, 3],
        }
    )
    _test_order(data)

    # based on https://github.com/datapane/datapane-hosted/issues/260
    data = pd.DataFrame(
        {
            "Countries": [1, 2, 3],
            "1961": [1, 2, 3],
            "1962": [1, 2, 3],
        }
    )
    _test_order(data)


def test_e2e_df_processing(tmp_path: Path):
    def _test_df(
        df: pd.DataFrame,
        expected_types_pd13: SList,
    ):
        df_conv = df.convert_dtypes()
        df_proc = process_df(df, copy=True)

        # check both df's have same nulls
        pd.testing.assert_frame_equal(pd.isnull(df), pd.isnull(df_conv))
        pd.testing.assert_frame_equal(pd.isnull(df), pd.isnull(df_proc))

        # check we can save and load processed file
        df2 = save_load_arrow(tmp_path, df_proc)
        pd.testing.assert_frame_equal(df_proc, df2)

        log.info(f"Using PD_VERSION={PD_VERSION}")
        expected_types = expected_types_pd13

        assert [str(x) for x in df2.dtypes] == expected_types

    # DF 1
    df = vd.data.cars()
    _test_df(df, ["string", "Float64", "UInt8", "Float64", "UInt8", "UInt16", "Float64", "datetime64[ns]", "category"])

    # DF 2 - float64/int64 downcasting for older pandas versions
    df = pd.DataFrame(
        dict(
            int_col=[x for x in range(30)],
            # NOTE - Pandas downcasting
            # ensure large ints remain if can't be downcasted
            int64_col=[x for x in range(29)] + [int(-1e10)],
            # handle invalid in downcasting for older pandas versions
            float64_int_col=[float(x) for x in range(29)] + [-1e2],  # int
            float64_int64_col=[float(x) for x in range(29)] + [-1e10],  # bigint
            float_col=[(x + 0.1) for x in range(30)],
        )
    )
    _test_df(
        df,
        # convert_dtypes doesn't convert Float64 -> Int64 on Windows
        ["UInt8", "Int64", "Int8", "Float64" if sys.platform == "win32" else "Int64", "Float64"],
    )

    # DF 3 - basic types
    df = pd.DataFrame(
        dict(
            str_col=[str(x) for x in range(30)],
            cat_col=["a" for x in range(30)],
            int_col=[x for x in range(30)],
            int64_col=[x for x in range(29)] + [int(-1e10)],
            float_col=[(x + 0.1) for x in range(30)],
            # store time as duration
            time_col=[timedelta(seconds=x) for x in range(30)],
            date_col=[datetime.utcnow() for x in range(30)],
            obj_col=[(str(x), str(x)) for x in range(30)],
            cat_obj_col=[("a", "b") for x in range(30)],
        )
    )
    _test_df(df, ["string", "category", "UInt8", "Int64", "Float64", "string", "datetime64[ns]", "string", "category"])

    # DF 4 - nullable
    df = pd.DataFrame(
        dict(
            str_col=[str(x) for x in range(30)] + [None, pd.NA],
            cat_col=["a" for x in range(30)] + [None, pd.NA],
            # int_col= [x for x in range(30)] + [pd.NA, pd.NA],
            int_na_col=[x for x in range(30)] + [np.nan, np.nan],
            float_col=[(x + 0.1) for x in range(30)] + [np.nan, np.nan],
            time_col=[timedelta(seconds=x) for x in range(30)] + [pd.NaT, pd.NaT],
            date_col=[datetime.utcnow() for x in range(30)] + [pd.NaT, pd.NaT],
        )
    )
    _test_df(df, ["string", "category", "UInt8", "Float64", "string", "datetime64[ns]"])
