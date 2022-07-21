"""Dataset Format handling"""
import abc
import enum
from typing import IO, Dict, Type, Union, cast

import pandas as pd
import pyarrow as pa
from pandas.errors import ParserError
from pyarrow import RecordBatchFileWriter

from .config import log
from .df_processor import process_df, str_to_arrow_str
from .dp_types import ARROW_EXT, ARROW_MIMETYPE, MIME
from .utils import guess_encoding


def write_table(table: pa.Table, sink: Union[str, IO[bytes]]):
    """Write an arrow table to a file"""
    writer = RecordBatchFileWriter(sink, table.schema)
    writer.write(table)
    writer.close()


PathOrFile = Union[str, IO]


class DFFormatter(abc.ABC):
    # TODO - tie to mimetypes lib
    content_type: MIME
    ext: str
    enum: str

    @staticmethod
    @abc.abstractmethod
    def load_file(fn: PathOrFile) -> pd.DataFrame:
        pass

    @staticmethod
    @abc.abstractmethod
    def save_file(fn: PathOrFile, df: pd.DataFrame):
        pass


DFFormatterCls = Type[DFFormatter]


class ArrowFormat(DFFormatter):
    content_type = ARROW_MIMETYPE
    ext = ARROW_EXT
    enum = "ARROW"

    @staticmethod
    def load_file(fn: PathOrFile) -> pd.DataFrame:
        df = pa.ipc.open_file(fn).read_pandas()
        str_to_arrow_str(df)
        return df

    @staticmethod
    def save_file(fn: PathOrFile, df: pd.DataFrame):
        df = process_df(df)
        # NOTE - can pass expected schema and columns for output df here
        table: pa.Table = pa.Table.from_pandas(df, preserve_index=False)
        write_table(table, fn)


class CSVFormat(DFFormatter):
    content_type = MIME("text/csv")
    ext = ".csv"
    enum = "CSV"

    @staticmethod
    def load_file(fn: PathOrFile) -> pd.DataFrame:
        fn = cast(str, fn)
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

    @staticmethod
    def save_file(fn: PathOrFile, df: pd.DataFrame):
        df.to_csv(fn, index=False)


class ExcelFormat(DFFormatter):
    content_type = MIME("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    ext = ".xlsx"
    enum = "EXCEL"

    @staticmethod
    def load_file(fn: PathOrFile) -> pd.DataFrame:
        return pd.read_excel(fn, engine="openpyxl")

    @staticmethod
    def save_file(fn: PathOrFile, df: pd.DataFrame):
        df.to_excel(fn, index=False, engine="openpyxl")


class DatasetFormats(enum.Enum):
    """Used to switch between the different format handlers"""

    CSV = CSVFormat
    EXCEL = ExcelFormat
    ARROW = ArrowFormat


# TODO - make into enums?
df_ext_map: Dict[str, DFFormatterCls] = {x.value.ext: x.value for x in DatasetFormats}
