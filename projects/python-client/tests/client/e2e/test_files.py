import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from matplotlib import pyplot as plt

import datapane as dp
from tests import check_df_equal

from .common import check_name, code, deletable, gen_df, gen_name

pytestmark = pytest.mark.usefixtures("dp_login")

df = gen_df()


# TODO - split these tests out and add export
@pytest.mark.org
def test_file_df():
    name = gen_name()

    # upload the file
    with deletable(dp.File.upload_df(df=df, name=name)) as b1:
        # are fields added?
        check_name(b1, name)
        # was the import as expected?
        assert b1.num_rows == 4
        assert b1.num_columns == 2
        assert b1.cells == 8

        # download
        df1 = b1.download_df()

        # is the exported df as expected?
        assert df1.size == b1.cells
        assert df1.shape == (b1.num_rows, b1.num_columns)
        check_df_equal(df1, df)

        # test obj lookup using name
        b2 = dp.File.get(b1.name)
        assert b2.name == b1.name
        # test obj lookup using id
        b3 = dp.File.by_id(b1.id)
        assert b3.name == b2.name


@pytest.mark.org
def test_file_csv_export(tmp_path: Path):
    # upload a df file
    b1 = dp.File.upload_df(df, name=gen_name())

    with deletable(b1):
        # export back to a csv and compare
        fn1 = tmp_path / "exported.csv"
        b1.download_file(fn1)
        df1 = pd.read_csv(fn1)
        check_df_equal(df, df1)
        # export back to excel and compare
        fn2 = tmp_path / "exported.xlsx"
        b1.download_file(fn2)
        df2 = pd.read_excel(fn2, engine="openpyxl")
        check_df_equal(df, df2)


@pytest.mark.org
def test_file_file(tmp_path: Path):
    # upload plain text
    fn = tmp_path / "initial.py"
    fn.write_text(code)
    b1 = dp.File.upload_file(fn, name=gen_name())
    with deletable(b1):
        # download as a file and compare
        fn1 = tmp_path / "exported.py"
        b1.download_file(fn1)
        code1 = Path(fn1).read_text()
        assert code1 == code

    # upload binary
    bin_code = code.encode()
    fn = tmp_path / "initial.bin"
    fn.write_bytes(bin_code)
    b1 = dp.File.upload_file(fn, name=gen_name())
    with deletable(b1):
        # download as a file and compare
        fn1 = tmp_path / "exported.bin"
        b1.download_file(fn1)
        bin_code1 = Path(fn1).read_bytes()
        assert bin_code1 == bin_code


@pytest.mark.org
def test_file_json(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    obj = {"foo": "bar"}
    # upload pickled object (this results in double-pickling)
    b1 = dp.File.upload_obj(data=pickle.dumps(obj), name=gen_name())
    # upload object
    b2 = dp.File.upload_obj(data=obj, name=gen_name())
    # upload object using JSON writer
    b3 = dp.File.upload_obj(data=obj, name=gen_name())
    with deletable(b1), deletable(b2), deletable(b3):
        # download objects
        # is the result of the uploaded pickle the same as the uploaded object?
        assert pickle.dumps(obj) == b1.download_obj()
        assert obj == b2.download_obj()
        assert obj == b3.download_obj()


@pytest.mark.org
def test_file_plot(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # upload mpl figure
    # Data for plotting
    plot_t = np.arange(0.0, 2.0, 0.01)
    plot_s = 1 + np.sin(2 * np.pi * plot_t)
    fig, ax = plt.subplots()
    ax.plot(plot_t, plot_s)
    b1 = dp.File.upload_obj(data=fig, name=gen_name())
    with deletable(b1):
        pass
