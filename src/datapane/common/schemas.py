"""Schema handling - this includes some obsolete code from the the previous Avro schema support"""
import re

import numpy as np
import pandas as pd

from datapane.common import SDict as DFSchema

# Removed functions to be rewritten
# essentially pre/post dataset & function specification schema compatibility checks/merges
# def add_optional_output_fields(specified: DFSchema, df: pd.DataFrame):
#     """Adds types deduced from `df.dtypes` to the schema preserving the order."""
# def merge_input_schemas(specified: DFSchema, embedded: DFSchema) -> None:
#     """Merges schemas by taking fields not present in the specified from the embedded schema."""


def fix_boolean_types(specified_schema: DFSchema, df: pd.DataFrame) -> None:
    """
    Convert nullable boolean columns to float for fields that are
    not specified or that are specified as floats
    """

    def is_null_bool(col: pd.Series) -> bool:
        """Determines whether a columns is a nullable boolean"""
        if col.dtype == np.dtype("O"):
            return col[col.notnull()].isin([True, False]).all()

        return False

    def is_float_type(type_):
        if sorted(type_) == ["double", "null"]:
            return True
        if sorted(type_) == ["float", "null"]:
            return True
        if type_ in ["float", "double"]:
            return True
        return False

    float_types = [x["name"] for x in specified_schema["fields"] if is_float_type(x["type"])]
    specified_fields_names = {f["name"] for f in specified_schema["fields"]}
    fields = [x for x in df.columns if x not in specified_fields_names or x in float_types]

    for col in fields:
        if is_null_bool(df[col]):
            df.loc[:, col] = df[col].astype(float)


def fix_mixed_types(writer_schema: DFSchema, df: pd.DataFrame) -> None:
    """Converts columns that are specified as strings to strings type."""
    for col in writer_schema["fields"]:
        if sorted(col["type"]) == ["null", "string"]:
            col_name = col["name"]
            df.loc[df[col_name].notnull(), col_name] = df[col_name][df[col_name].notnull()].astype(
                str
            )
            # np.nan is not of type ["string", "null"] as it is a float thus needs to be None
            df.loc[df[col_name].isnull(), col_name] = None


def fix_col_names(data: pd.DataFrame) -> None:
    """
    Rename the cols of a dataframe.
    NOTE - obsolete & unused, was needed to support Avro col names but may be useful in future.
    """

    # all the (renamed) columns we have processed:
    seen_cols = set()
    # build a list of all columns and their first occurance
    # in the column list. When we check for existance in the original
    # columns we will end up with false-positives by encountering ourself.
    # Using the index we easily check for duplicates that appear after our
    # position. We do this once, rather than, eg, taking a slice of the original
    # columns for each check:
    columns = {}
    for i, col in enumerate(data.columns):
        if not isinstance(col, str):
            col = str(col)
        if col not in columns:
            # first occurance
            columns[col] = i

    def process_col_name(num, col_name) -> str:
        disallowed_pattern = re.compile(r"\W")
        new_col_name = disallowed_pattern.sub("_", col_name)

        # first letter can't be an integer
        if new_col_name[0].isdigit():
            new_col_name = "_" + new_col_name

        # avoids creating duplicate names
        prefix = new_col_name
        suffix = 0
        while True:
            suffix += 1
            # check previously renamed columns...
            if new_col_name in seen_cols or (
                # or columns remaining to be renamed....
                new_col_name in columns
                and columns[new_col_name] > num
            ):
                new_col_name = prefix + "_" + str(suffix)
            else:
                break

        seen_cols.add(new_col_name)
        return new_col_name

    new_cols = [process_col_name(i, str(col)) for i, col in enumerate(data.columns)]
    data.columns = new_cols
