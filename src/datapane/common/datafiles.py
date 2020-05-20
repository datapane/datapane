import abc
import enum
import os
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Dict, Optional, TextIO, Type, Union

import pandas as pd
import pyarrow as pa
from pandas.errors import ParserError
from pyarrow import RecordBatchFileWriter

from .config import log
from .df_processor import process_df
from .dp_types import ARROW_EXT, ARROW_MIMETYPE, MIME, Hash

# TODO - cleanup and refactor functions


@dataclass
class ImportFileResp:
    cas_ref: Hash
    content_type: MIME
    file_size: int
    num_rows: int
    num_columns: int


def convert_df_table(df: pd.DataFrame) -> pa.Table:
    process_df(df)
    # NOTE - can pass expected schema and columns for output df here
    table: pa.Table = pa.Table.from_pandas(df, preserve_index=False)
    return table


def convert_csv_table(
    _input: Union[str, TextIO], output: Optional[Union[str, BinaryIO]] = None, ext: str = ".csv"
) -> pa.Table:
    """Convert & return csv/excel file to an arrow table via pandas, optionally writing it disk"""
    df = df_ext_map[ext].load_file(fn=_input)
    table = convert_df_table(df)
    if output is not None:
        write_table(table, output)
    return table


def import_arrow_file(table: pa.Table, arrow_f_name: str, cas_ref: str = None) -> ImportFileResp:
    file_size = os.path.getsize(arrow_f_name)
    # schema unused atm
    _: pa.Schema = table.schema

    return ImportFileResp(
        cas_ref=cas_ref,
        content_type=ARROW_MIMETYPE,
        file_size=file_size,
        num_rows=table.num_rows,
        num_columns=table.num_columns,
    )


def import_from_csv(in_f_path: Path, arrow_f_name: str) -> pa.Table:
    """
    Import a local file to a local arrow file,
    we use filenames rather than open files as pyarrow docs mention it's more performant
    """
    ext: str = "".join(in_f_path.suffixes)
    # pull imported file and read into an arrow table
    table = convert_csv_table(str(in_f_path), arrow_f_name, ext=ext)
    log.debug(f"Imported CSV file of size {table.shape} with following schema: \n{table.schema}")
    return table


def import_local_file_from_disk(in_f_path: Path, arrow_f_name: str) -> ImportFileResp:
    table = import_from_csv(in_f_path, arrow_f_name)
    return import_arrow_file(table, arrow_f_name)


def write_table(table: pa.Table, sink: Union[str, BinaryIO]):
    """Write an arrow table to a file"""
    writer = RecordBatchFileWriter(sink, table.schema)
    writer.write(table)
    writer.close()


####################################################################################################
# Dataset Format handling
class DFFormatter(abc.ABC):
    # TODO - tie to mimetypes lib
    content_type: MIME
    ext: str
    enum: str

    @staticmethod
    @abc.abstractmethod
    def load_file(fn: str) -> pd.DataFrame:
        ...

    @staticmethod
    @abc.abstractmethod
    def save_file(fn: str, df: pd.DataFrame):
        ...


DFFormatterCls = Type[DFFormatter]


class ArrowFormat(DFFormatter):
    content_type = ARROW_MIMETYPE
    ext = ARROW_EXT
    enum = "ARROW"

    def load_file(fn: str) -> pd.DataFrame:
        return pa.ipc.open_file(fn).read_pandas()

    def save_file(fn: str, df: pd.DataFrame):
        table = convert_df_table(df)
        write_table(table, fn)


class CSVFormat(DFFormatter):
    content_type = "text/csv"
    ext = ".csv"
    enum = "CSV"

    def load_file(fn: str) -> pd.DataFrame:
        try:
            return pd.read_csv(fn, engine="c", sep=",")
        except ParserError as e:
            log.warning(f"Error parsing CSV file ({e}), trying python fallback")
            return pd.read_csv(fn, engine="python", sep=None)

    def save_file(fn: str, df: pd.DataFrame):
        df.to_csv(fn, index=False)


class ExcelFormat(DFFormatter):
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ext = ".xlsx"
    enum = "EXCEL"

    def load_file(fn: str) -> pd.DataFrame:
        return pd.read_excel(fn, engine="openpyxl")

    def save_file(fn: str, df: pd.DataFrame):
        df.to_excel(fn, index=False, engine="openpyxl")


class DatasetFormats(enum.Enum):
    """Used to switch between the different format handlers"""

    CSV = CSVFormat
    EXCEL = ExcelFormat
    ARROW = ArrowFormat


# TODO - make into enums?
df_ext_map: Dict[str, DFFormatterCls] = {x.value.ext: x.value for x in DatasetFormats}
