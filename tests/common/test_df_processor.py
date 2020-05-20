from typing import List

import pandas as pd

from datapane.common.df_processor import convert_csv_pd, parse_categories, parse_dates


def _check_dates_parsed(df: pd.DataFrame, date_columns: List[str]):
    assert set(list(df.select_dtypes("datetime").columns)) == set(date_columns)


def _check_categories_parsed(df: pd.DataFrame, categorical_columns: List[str]):
    assert set(list(df.select_dtypes("category").columns)) == set(categorical_columns)


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
