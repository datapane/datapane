"""
Dynamic handling for optional libraries - this module is imported on demand
"""
# flake8: noqa:F811 isort:skip_file
from __future__ import annotations

from packaging import version as v
from packaging.specifiers import SpecifierSet

from datapane.client import log

# NOTE - need to update this and keep in sync with JS
BOKEH_V_SPECIFIER = SpecifierSet("~=2.4.2")
PLOTLY_V_SPECIFIER = SpecifierSet(">=4.0.0")
FOLIUM_V_SPECIFIER = SpecifierSet(">=0.12.0")


def _check_version(name: str, _v: v.Version, ss: SpecifierSet):
    if _v not in ss:
        log.warning(
            f"{name} version {_v} is not supported, these plots may not display correctly, please install version {ss}"
        )


# Optional Plotting library import handling
# Matplotlib
try:
    from matplotlib.figure import Axes, Figure
    from numpy import ndarray

    HAVE_MATPLOTLIB = True
except ImportError:
    log.debug("No matplotlib found")
    HAVE_MATPLOTLIB = False

# Folium
try:
    import folium
    from folium import Map

    _check_version("Folium", v.Version(folium.__version__), FOLIUM_V_SPECIFIER)
    HAVE_FOLIUM = True
except ImportError:
    HAVE_FOLIUM = False
    log.debug("No folium found")

# Bokeh
try:
    import bokeh
    from bokeh.layouts import LayoutDOM as BLayout
    from bokeh.plotting.figure import Figure as BFigure

    _check_version("Bokeh", v.Version(bokeh.__version__), BOKEH_V_SPECIFIER)
    HAVE_BOKEH = True
except ImportError:
    HAVE_BOKEH = False
    log.debug("No Bokeh Found")

# Plotly
try:
    import plotly
    from plotly.graph_objects import Figure as PFigure

    _check_version("Plotly", v.Version(plotly.__version__), PLOTLY_V_SPECIFIER)
    HAVE_PLOTLY = True
except ImportError:
    HAVE_PLOTLY = False
    log.debug("No Plotly Found")
