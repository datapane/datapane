"""Type-driven block wrapping"""
# flake8: noqa:F811
from __future__ import annotations

import typing as t
from pathlib import Path

import pandas as pd
from altair.utils import SchemaBase
from multimethod import multimethod

from datapane import blocks as b
from datapane import optional_libs as opt
from datapane.client import DPClientError

from .base import DataBlock


@multimethod
def convert_to_block(x: object) -> DataBlock:
    raise DPClientError(
        f"{type(x)} not supported directly, please pass into in the appropriate dp object (including dp.Attachment if want to upload as a pickle)"
    )


# NOTE - this is currently disabled to avoid confusing users when they
# try to embed any Python object, instead they must use dp.Attachment
# @multimethod
# def convert_to_block(x: t.Any) -> DataBlock:
#     return b.Attachment(x)


@multimethod
def convert_to_block(x: str) -> DataBlock:
    return b.Text(x)


@multimethod
def convert_to_block(x: Path) -> DataBlock:
    return b.Attachment(file=x)


@multimethod
def convert_to_block(x: pd.DataFrame) -> DataBlock:
    n_cells = x.shape[0] * x.shape[1]
    return b.Table(x) if n_cells <= 250 else b.DataTable(x)


# Plots
@multimethod
def convert_to_block(x: SchemaBase) -> DataBlock:
    return b.Plot(x)


if opt.HAVE_BOKEH:

    @multimethod
    def convert_to_block(x: t.Union[opt.BFigure, opt.BLayout]) -> DataBlock:
        return b.Plot(x)


if opt.HAVE_PLOTLY:

    @multimethod
    def convert_to_block(x: opt.PFigure) -> DataBlock:
        return b.Plot(x)


if opt.HAVE_FOLIUM:

    @multimethod
    def convert_to_block(x: opt.Map) -> DataBlock:
        return b.Plot(x)


if opt.HAVE_MATPLOTLIB:

    @multimethod
    def convert_to_block(x: t.Union[opt.Figure, opt.Axes, opt.ndarray]) -> DataBlock:
        return b.Plot(x)
