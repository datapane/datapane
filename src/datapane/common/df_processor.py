import datetime
from numbers import Number
from typing import Any

import numpy as np
import pandas as pd


def convert_indices(df: pd.DataFrame):
    """
    extract all indices to columns if all are not numerical
    and don't clash with existing column names
    """
    if df.index.nlevels > 1:
        # always reset multi-index
        df.reset_index(inplace=True)
    elif df.index.dtype == np.dtype("int64"):
        # Int64Index -> RangeIndex if possible
        df.reset_index(inplace=True, drop=True)

    # col_names: List[str] = df.columns.values.tolist()
    # if (
    #     all([df.index.get_level_values(x).dtype != np.dtype("int64") for x in range(df.index.nlevels)])
    #     and len(set(df.index.names)) == len(df.index.names)
    #     and not any([x in col_names for x in df.index.names])
    # ):
    #     df.reset_index(inplace=True)


def downcast_numbers(data: pd.DataFrame):
    """Downcast numerics"""

    def downcast(ser: pd.Series) -> pd.Series:
        try:
            ser = pd.to_numeric(ser, downcast="signed")
            ser = pd.to_numeric(ser, downcast="unsigned")
        except Exception:
            pass  # catch failure on Int64Dtype
        return ser

    # A result of downcast(timedelta64[ns]) is int <ns> and hard to understand.
    # e.g.) 0 days 00:54:38.777572 -> 3278777572000 [ns]
    df_num = data.select_dtypes("number", exclude=["timedelta"])  # , pd.Int64Dtype])
    data[df_num.columns] = df_num.apply(downcast)


def timedelta_to_str(df: pd.DataFrame):
    """
    convert timedelta to str - NOTE - only until arrow.js supports Duration type
    """
    df_td = df.select_dtypes("timedelta")
    # df[df_timedelta.columns] = df_timedelta.astype("string")
    df[df_td.columns] = np.where(pd.isnull(df_td), pd.NA, df_td.astype("string"))


def parse_categories(data: pd.DataFrame):
    """Detect and converts categories"""

    def criteria(ser: pd.Series) -> bool:
        """Decides whether to convert into categorical"""
        nunique: int = ser.nunique()

        if nunique <= 20 and (nunique != ser.size):
            # few unique values => make it a category regardless of the proportion
            return True

        prop_unique = (nunique + 1) / (ser.size + 1)  # + 1 for nan

        if prop_unique <= 0.05:
            # a lot of redundant information => categories are more compact
            return True

        return False

    def try_to_category(ser: pd.Series) -> pd.Series:
        return ser.astype("category") if criteria(ser) else ser

    potential_cats = data.select_dtypes(["string", "object"])
    data[potential_cats.columns] = potential_cats.apply(try_to_category)


def obj_to_str(df: pd.DataFrame):
    """Converts remaining objects columns to str"""
    # convert objects to str / NA
    df_str = df.select_dtypes("object")
    # df[df_str.columns] = np.where(pd.isnull(df_str), pd.NA, df_str.astype("string"))
    df[df_str.columns] = df_str.astype("string")

    # convert categorical values (as strings if object)
    def to_str_cat_vals(x: pd.Series) -> pd.Series:
        if x.cat.categories.dtype == np.dtype("object"):
            # x.cat.categories = x.cat.categories.astype(str)
            # x.cat.categories = np.where(pd.isnull(x.cat.categories), pd.NA, x.cat.categories.astype("string"))
            x.cat.categories = x.cat.categories.astype("string")
        return x

    df_cat = df.select_dtypes("category")
    df[df_cat.columns] = df_cat.apply(to_str_cat_vals)


def process_df(df: pd.DataFrame, copy: bool = False) -> pd.DataFrame:
    """
    Processing steps needed before writing / after reading
    We only modify the dataframe to optimise size,
    rather than convert/infer types, e.g. no longer parsing dates from strings

    NOTE - this mutates the dataframe by default
    """
    if copy:
        df = df.copy(deep=True)

    convert_indices(df)

    # convert timedelta
    timedelta_to_str(df)

    downcast_numbers(df)
    # save timedeltas cols (unneeded whilst timedelta_to_str used)
    # td_col = df.select_dtypes("timedelta")
    df = df.convert_dtypes()
    # df[td_col.columns] = td_col
    obj_to_str(df)
    parse_categories(df)
    return df


def to_df(value: Any) -> pd.DataFrame:
    """
    Converts a python object, i.e. a script's output, to a dataframe
    NOTE - this returns a new DF each time
    """
    if value is None:
        # This return the empty dataframe, which atm is the same as
        # the empty file object in the CAS.
        # However this is not ensured as pyarrow changes
        return pd.DataFrame()

    if isinstance(value, pd.DataFrame):
        return value.copy(deep=True)

    if isinstance(value, (pd.Series, pd.Index)):
        if value.name is not None:
            return pd.DataFrame(value)

        return pd.DataFrame({"Result": value})

    if isinstance(value, (Number, str, bool, datetime.datetime, datetime.timedelta)):
        return pd.DataFrame({"Result": value}, index=[0])

    if isinstance(value, np.ndarray):
        try:
            out_df = pd.DataFrame(value)
        except ValueError:
            squeezed = np.squeeze(value)
            if squeezed.shape == ():
                # must be a scalar
                out_df = pd.DataFrame({"Result": squeezed}, index=[0])
            else:
                out_df = pd.DataFrame(squeezed)

        if out_df.columns.tolist() == [0]:
            out_df.columns = ["Result"]

        return out_df

    raise ValueError("Must return a primitive, pd.DataFrame, pd.Series or numpy array.")


TRUNCATE_CELLS = 10000
TRUNCATE_ROWS = 1000


def truncate_dataframe(df: pd.DataFrame, max_rows=TRUNCATE_ROWS, max_cells=TRUNCATE_CELLS) -> pd.DataFrame:
    """Truncate a pandas dataframe if needed"""
    rows, cols = df.shape
    # determine max rows to truncate df to based on max cells and df cols
    cols = cols or 1  # handle empty df
    max_rows = min(max_rows, int(max_cells / cols))
    # return non-truncated preview if df smaller than max rows allowed
    if rows <= max_rows:
        return df
    # truncate df to fit max cells
    if not isinstance(df.index, pd.RangeIndex):
        raise ValueError("Dataframe has unsupported index type")
    return df.truncate(before=0, after=max_rows - 1, copy=False)
