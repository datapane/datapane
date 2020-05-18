import pickle
from pathlib import Path
from typing import List, Optional

import numpy as np
import pytest
from matplotlib import pyplot as plt
from tests import check_df_equal

import datapane as dp
from datapane.client import api
from datapane.common import temp_fname

from .common import code, gen_df, gen_name

pytestmark = pytest.mark.usefixtures("dp_login")


# TODO - split these tests out
def test_blob():
    blob1: Optional[dp.Blob] = None
    created_blobs: List[dp.Blob] = []
    try:
        df = gen_df()
        name = gen_name()
        visibility = "PUBLIC"

        # upload the blob
        blob1 = api.Blob.upload_df(df=df, visibility=visibility, name=name)
        created_blobs.append(blob1)

        # upload a csv file
        with temp_fname(".csv") as fn:
            df.to_csv(fn)
            blob2 = api.Blob.upload_file(fn, name=gen_name())
            created_blobs.append(blob2)

        # upload plain text
        with temp_fname(".py") as fn:
            fn = Path(fn)
            fn.write_text(code)
            blob3 = api.Blob.upload_file(fn, name=gen_name())
            created_blobs.append(blob3)

        # upload pickled object
        obj = {"foo": "bar"}
        pkl = pickle.dumps(obj)
        blob4 = api.Blob.upload_obj(data=pkl, name=gen_name())
        created_blobs.append(blob4)

        # upload object
        blob5 = api.Blob.upload_obj(data=obj, name=gen_name())
        created_blobs.append(blob5)

        # upload object using JSON writer
        blob6 = api.Blob.upload_obj(data=obj, is_json=True, name=gen_name())
        created_blobs.append(blob6)

        # upload mpl figure
        # Data for plotting
        plot_t = np.arange(0.0, 2.0, 0.01)
        plot_s = 1 + np.sin(2 * np.pi * plot_t)
        fig, ax = plt.subplots()
        ax.plot(plot_t, plot_s)
        blob7 = api.Blob.upload_obj(data=fig, visibility=visibility, name=gen_name())
        created_blobs.append(blob7)

        # download objects
        obj4 = blob4.download_obj()
        obj5 = blob5.download_obj()
        obj6 = blob6.download_obj()
        # is the result of the uploaded pickle the same as the uploaded object?
        assert obj4 == obj
        assert obj5 == obj
        assert obj6 == obj

        # are fields added?
        assert blob1.name == name
        # was the import as expected?
        assert blob1.num_rows == 4
        assert blob1.num_columns == 2
        assert blob1.cells == 8
        assert blob1.visibility == "PUBLIC"

        # download
        df1 = blob1.download_df()

        # is the exported df as expected?
        assert df1.size == blob1.cells
        assert df1.shape == (blob1.num_rows, blob1.num_columns)
        check_df_equal(df1, df)

        # test obj lookup
        blob1a = api.Blob(blob1.name)

        assert blob1a.name == blob1.name
        # test obj lookup using id
        blob1b = api.Blob(id_or_url=blob1.id)
        assert blob1b.name == blob1a.name

    finally:
        for blob in created_blobs:
            blob.delete()
        # check it has been deleted
        if blob1:
            with pytest.raises(api.HTTPError) as _:
                _ = api.Blob(blob1.name)
