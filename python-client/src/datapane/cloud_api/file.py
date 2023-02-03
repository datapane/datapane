from __future__ import annotations

import json
import os
import pickle
import typing as t
from pathlib import Path

import pandas as pd

from datapane.client import DPClientError, log
from datapane.common import PKL_MIMETYPE, ArrowFormat, NPath
from datapane.common.datafiles import DFFormatterCls, df_ext_map
from datapane.common.df_processor import to_df

from .common import DPTmpFile, do_download_file
from .dp_object import DPObjectRef


def save_df(df: pd.DataFrame) -> DPTmpFile:
    """Export a df for uploading"""
    fn = DPTmpFile(ArrowFormat.ext)

    # create a copy of the df to process
    df = to_df(df)
    if df.size == 0:
        raise DPClientError("Empty DataFrame provided")

    # process_df called in Arrow.save_file
    # process_df(df)
    ArrowFormat.save_file(fn.name, df)
    log.debug(f"Saved df to {fn} ({os.path.getsize(fn.file)} bytes)")
    return fn


class File(DPObjectRef):
    """
    Files are files that can be uploaded and downloaded for use in your apps,
    for instance trained models, datasets, and (pickled) Python objects.
    They are generally large, but can be any size.

    Attributes:
        content_type: the file content-type
        size_bytes: the file size
        num_rows: number of rows in the file (if a dataframe)
        num_colums: number of colums in the file (if a dataframe)
        cells: number of cells in the file (if a dataframe)
        overwrite: overwrite the file in project

    ..tip:: Use the static methods to create `Files` rather than the constructor
    """

    endpoint: str = "/files/"

    @classmethod
    def upload_df(cls, df: pd.DataFrame, **kwargs) -> File:
        """
        Create a file containing the dataframe provided

        Args:
            df: The pandas dataframe to upload as a File

        Returns:
            An instance of the created `File` object
        """
        with save_df(df) as fn:
            return cls.post_with_files(file=fn.file, **kwargs)

    @classmethod
    def upload_file(cls, fn: NPath, **kwargs) -> File:
        """
        Create a file containing the contents of the file provided

        Args:
            fn: Path to the file to upload as a File

        Returns:
            An instance of the created `File` object
        """
        return cls.post_with_files(file=Path(fn), **kwargs)

    @classmethod
    def upload_obj(cls, data: t.Any, **kwargs) -> File:
        """
        Create a file containing the contents of the Python object provided,
        the object may be pickled or converted to JSON before storing.

        Args:
            data: Python object to upload as a File

        Returns:
            An instance of the created `File` object
        """
        # import here as a very slow module due to nested imports
        from .obsolete.files import save

        fn = save(data)
        return cls.post_with_files(file=fn.file, **kwargs)

    def download_df(self) -> pd.DataFrame:
        """
        Download the file and return it as a Dataframe

        Returns:
            A pandas dataframe generated from the file
        """
        with DPTmpFile(ArrowFormat.ext) as fn:
            do_download_file(self.data_url, fn.name)
            return ArrowFormat.load_file(fn.name)

    def download_file(self, fn: NPath) -> None:
        """
        Download the file to the file provided

        Args:
            fn: Path representing the location to save the file
        """
        fn = t.cast(Path, fn)

        def get_export_format() -> DFFormatterCls:
            filename = t.cast(Path, fn)
            ext = filename.suffix
            if ext not in df_ext_map:
                raise DPClientError(
                    f"Extension {ext} not valid for exporting table. Must be one of {', '.join(df_ext_map.keys())}"
                )
            return df_ext_map[ext]

        # If file is of arrow type, export it. Otherwise, download the url directly.
        if self.content_type == ArrowFormat.content_type:
            # download as a arrow->df, then export on the client
            df = self.download_df()
            fmt = get_export_format()
            fmt.save_file(str(fn), df)
        else:
            do_download_file(self.data_url, fn)

    def download_obj(self) -> t.Any:
        """
        Download the file and return it as a Python object

        Returns:
            The object created by deserialising the File (either via Pickle or JSON decoding)
        """
        with DPTmpFile(".obj") as fn:
            do_download_file(self.data_url, fn.name)
            # In the case that the original object was a Python object or bytes-like object,
            # the downloaded obj will be a pickle which needs to be unpickled.
            # Otherwise it's a stringified JSON object (e.g. an Altair plot) that can be returned as JSON.
            if self.content_type == PKL_MIMETYPE:
                with fn.file.open("rb") as fp:
                    return pickle.load(fp)
            else:
                return json.loads(fn.file.read_text())
