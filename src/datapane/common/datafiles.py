import abc
import enum
import os
from dataclasses import dataclass
from typing import BinaryIO, Dict, Type, Union

import pandas as pd
import pyarrow as pa
from pandas.errors import ParserError
from pyarrow import RecordBatchFileWriter

from .config import log
from .df_processor import process_df
from .dp_types import ARROW_EXT, ARROW_MIMETYPE, MIME, Hash
from .utils import guess_encoding


@dataclass
class ImportFileResp:
    cas_ref: Hash
    content_type: MIME
    file_size: int
    num_rows: int
    num_columns: int


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
        df = process_df(df)
        # NOTE - can pass expected schema and columns for output df here
        table: pa.Table = pa.Table.from_pandas(df, preserve_index=False)
        write_table(table, fn)


class CSVFormat(DFFormatter):
    content_type = "text/csv"
    ext = ".csv"
    enum = "CSV"

    def load_file(fn: str) -> pd.DataFrame:

        try:
            return pd.read_csv(fn, engine="c", sep=",")
        except UnicodeDecodeError:
            encoding = guess_encoding(fn)
            return pd.read_csv(fn, engine="c", sep=",", encoding=encoding)
        except ParserError as e:
            log.warning(f"Error parsing CSV file ({e}), trying python fallback")
            try:
                return pd.read_csv(fn, engine="python", sep=None)
            except UnicodeDecodeError:
                encoding = guess_encoding(fn)
                return pd.read_csv(fn, engine="python", sep=None, encoding=encoding)

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
