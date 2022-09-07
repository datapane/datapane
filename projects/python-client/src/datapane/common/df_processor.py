import datetime
from numbers import Number
from typing import Any

import numpy as np
import pandas as pd
from packaging.specifiers import SpecifierSet
from packaging.version import Version

PD_VERSION = Version(pd.__version__)
PD_1_3_GREATER = SpecifierSet(">=1.3.0")
PD_1_2_x = SpecifierSet("~=1.2.0")
PD_1_1_x = SpecifierSet("~=1.1.0")


def convert_axis(df: pd.DataFrame):
    """flatten both columns and indexes"""

    # flatten hierarchical columns and convert to strings
    if df.columns.nlevels > 1:
        df.columns = ["/".join(a) for a in df.columns.to_flat_index()]

    df.columns = df.columns.astype("string")

    # flatten/reset indexes
    if isinstance(df.index, pd.RangeIndex):
        pass  # allow RangeIndex - reset numbers?
    elif isinstance(df.index, pd.Int64Index):
        df.reset_index(inplace=True, drop=True)
    else:
        # reset if any other index type, e.g. MultiIndex, custom Index
        # all new column dtypes will converted in latter functions
        df.reset_index(inplace=True)


def downcast_numbers(data: pd.DataFrame):
    """Downcast numerics"""

    def downcast_ints(ser: pd.Series) -> pd.Series:
        try:
            ser = pd.to_numeric(ser, downcast="signed")
            ser = pd.to_numeric(ser, downcast="unsigned")
        except Exception:
            pass  # catch failure on Int64Dtype
        return ser

    # A result of downcast(timedelta64[ns]) is int <ns> and hard to understand.
    # e.g.) 0 days 00:54:38.777572 -> 3278777572000 [ns]
    df_num = data.select_dtypes("integer", exclude=["timedelta"])  # , pd.Int64Dtype])
    data[df_num.columns] = df_num.apply(downcast_ints)

    def downcast_floats(ser: pd.Series) -> pd.Series:
        ser = pd.to_numeric(ser, downcast="float", errors="ignore")
        return ser

    # float downcasting currently disabled - alters values (both float64 and int64) and rounds to 'inf' instead of erroring
    # see https://github.com/pandas-dev/pandas/issues/19729
    # df_num = data.select_dtypes("floating")
    # data[df_num.columns] = df_num.apply(downcast_floats)


def timedelta_to_str(df: pd.DataFrame):
    """
    convert timedelta to str
    NOTE - only until arrow.js supports Duration type
    """
    df_td = df.select_dtypes("timedelta")
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
    df[df_str.columns] = df_str.astype("string")

    # convert categorical values (as strings if object)
    def to_str_cat_vals(x: pd.Series) -> pd.Series:
        if x.cat.categories.dtype == np.dtype("object"):
            x.cat.categories = x.cat.categories.astype("string")
        return x

    df_cat = df.select_dtypes("category")
    df[df_cat.columns] = df_cat.apply(to_str_cat_vals)


def bipartite_to_bool(df: pd.DataFrame):
    # This was removed from our processing steps as some users required the numerical representation of binary columns.
    """Converts biperatite numeric {0, 1} columns to bool."""
    # Get names of numeric columns with only 2 unique values.
    df_num = df.select_dtypes("integer", exclude=["timedelta"])
    bipartite_columns = df_num.columns[df_num.dropna().nunique() == 2]

    for column in bipartite_columns:
        series = df[column]

        # Only apply the type change to {0, 1} columns
        val_range = series.min(), series.max()
        val_min, val_max = val_range[0], val_range[1]

        if val_min == 0 and val_max == 1:
            df[column] = df[column].astype(bool)


def str_to_arrow_str(df: pd.DataFrame):
    """Use the memory-efficient pyarrow string dtype (pandas >= 1.3 only)"""
    # convert objects to str / NA
    if PD_VERSION in PD_1_3_GREATER:
        df_str = df.select_dtypes("string")
        df[df_str.columns] = df_str.astype("string[pyarrow]")


def process_df(df: pd.DataFrame, copy: bool = False) -> pd.DataFrame:
    """
    Processing steps needed before writing / after reading
    We only modify the dataframe to optimise size,
    rather than convert/infer types, e.g. no longer parsing dates from strings

    NOTE - this mutates the dataframe by default but returns it - use the returned copy!
    """
    if copy:
        df = df.copy(deep=True)

    convert_axis(df)

    # convert timedelta
    timedelta_to_str(df)

    # NOTE - pandas >= 1.3 handles downcasting of nullable values correctly
    if PD_VERSION in PD_1_3_GREATER:
        df = df.convert_dtypes()
        downcast_numbers(df)
    else:
        # downcast first as can't downcast Int64 correctly after
        downcast_numbers(df)
        # convert all non-floating vals

        non_f = df.select_dtypes(exclude="floating")
        # pandas version < 1.3 raises ValueError when running convert_dtypes on empty dataframes so we need to check it
        if len(non_f.columns) > 0:
            df[non_f.columns] = non_f.convert_dtypes()
        # convert all floating vals, but disable float64->int64 conversioon
        f = df.select_dtypes(include="floating")
        if len(f.columns) > 0:
            df[f.columns] = f.convert_dtypes(convert_integer=False)

    # save timedeltas cols (unneeded whilst timedelta_to_str used)
    # td_col = df.select_dtypes("timedelta")
    # df[td_col.columns] = td_col
    obj_to_str(df)
    parse_categories(df)

    # convert all strings to use the arrow dtype
    str_to_arrow_str(df)

    return df


def to_df(value: Any) -> pd.DataFrame:
    """
    Converts a python object, i.e. a app's output, to a dataframe
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


def truncate_dataframe(
    df: pd.DataFrame, max_rows: int = TRUNCATE_ROWS, max_cells: int = TRUNCATE_CELLS
) -> pd.DataFrame:
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
