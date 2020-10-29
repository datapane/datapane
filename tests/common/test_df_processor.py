from typing import List

import pandas as pd
import pytest

from datapane.common.df_processor import (
    convert_csv_pd,
    downcast_numbers,
    parse_categories,
    parse_dates,
    parse_timedelta,
    to_str,
)


def _check_dates_parsed(df: pd.DataFrame, date_columns: List[str]):
    assert set(list(df.select_dtypes("datetime").columns)) == set(date_columns)


def _check_categories_parsed(df: pd.DataFrame, categorical_columns: List[str]):
    assert set(list(df.select_dtypes("category").columns)) == set(categorical_columns)


def _check_timedelta_parsed(df: pd.DataFrame, timedelta_columns: List[str]):
    assert set(list(df.select_dtypes("timedelta").columns)) == set(timedelta_columns)


def _check_is_object(df: pd.DataFrame, object_columns: List[str]):
    assert set(list(df.select_dtypes("object").columns)) == set(object_columns)


def test_parse_dates_regular():
    data = convert_csv_pd(
        """
        data_col1,data_col2,float_col,string_col
        2017-01-10,2017-01-21T23:10:24,0.23,bla1
        2017-01-11,2017-01-23T23:01:24,0.23,bla1
        """
    )
    parse_dates(data)
    _check_dates_parsed(data, ["data_col1", "data_col2"])


def test_parse_dates_empty():
    _check_dates_parsed(pd.DataFrame(), [])


def test_parse_dates_wrong_date():
    data = convert_csv_pd(
        """
        data_col1,data_col2,float_col,string_col
        2017-01-10,2017-01-21T23:10:24,0.23,bla1
        2017-01-1s,2017-01-23T23:01:24,0.23,bla1
        """
    )
    parse_dates(data)
    _check_dates_parsed(data, ["data_col2"])


def test_parse_dates_nulls():
    # NOTE - using just Z, not .000Z means pandas doesn't infer timezone, so naive datetime object
    data = convert_csv_pd(
        """
        timestamp,value
        2019-02-19T03:00:02Z,1
        ,2
        2019-01-10T12:10:10Z,3
        """
    )
    parse_dates(data)
    _check_dates_parsed(data, ["timestamp"])


def test_parse_timedelta_regular():
    data = convert_csv_pd(
        """
        timedelta_col,float_col,string_col
        "1 day, 4:08:25.159814",0.23,bla1
        "1 day, 18:34:16.196687",0.23,bla1
        """
    )
    parse_timedelta(data)
    _check_timedelta_parsed(data, ["timedelta_col"])


def test_parse_timedelta_with_assertion_error():
    data = convert_csv_pd(
        """
        timedelta_col1,timedelta_col2,float_col,string_col
        4:08:25.159814,"1 day, 4:08:25.159814",0.23,bla1
        18:34:16.196687,"1 day, 18:34:16.196687",0.23,bla1
        """
    )
    parse_timedelta(data)
    # timedelta_col1's dtype is a datetime64[ns]
    _check_dates_parsed(data, ["timedelta_col1"])
    with pytest.raises(AssertionError):
        _check_timedelta_parsed(data, ["timedelta_col1", "timedelta_col2"])


def test_parse_timedelta_explicit_convert():
    def convert_csv_pd_(string: str) -> pd.DataFrame:
        import textwrap
        from io import StringIO

        from datapane.common.df_processor import process_df

        buf = StringIO(textwrap.dedent(string).strip())
        df = pd.read_csv(buf, engine="c", sep=",")
        df["timedelta_col1"] = pd.to_timedelta(df["timedelta_col1"])
        process_df(df)
        return df

    # timedelta_col1 is parsed by `parse_dates` unless it is converted explicitly
    data = convert_csv_pd_(
        """
        timedelta_col1,timedelta_col2,float_col,string_col
        4:08:25.159814,"1 day, 4:08:25.159814",0.23,bla1
        18:34:16.196687,"1 day, 18:34:16.196687",0.23,bla1
        """
    )
    parse_timedelta(data)
    _check_timedelta_parsed(data, ["timedelta_col1", "timedelta_col2"])


def test_parse_categories():
    data = convert_csv_pd(
        """
        str1,str2
        a1,a1
        2,2
        3,3
        4,4
        5,5
        6,6
        7,7
        8,8
        9,9
        10,10
        11,11
        12,12
        13,13
        14,14
        15,15
        16,16
        17,17
        18,18
        19,19
        20,20
        21,20
        """
    )
    parse_categories(data)
    _check_categories_parsed(data, ["str2"])


def test_downcast_numbers_timedelta():
    data = convert_csv_pd(
        """
        timedelta_col,float_col,string_col
        "1 day, 4:08:25.159814",0.23,bla1
        "1 day, 18:34:16.196687",0.23,bla1
        """
    )
    parse_timedelta(data)
    downcast_numbers(data)
    _check_timedelta_parsed(data, ["timedelta_col"])


def test_to_str_timedelta():
    data = convert_csv_pd(
        """
        timedelta_col,float_col,string_col
        "1 day, 4:08:25.159814",0.23,bla1
        "1 day, 18:34:16.196687",0.23,bla1
        """
    )
    parse_timedelta(data)
    to_str(data)
    _check_is_object(data, ["timedelta_col"])
