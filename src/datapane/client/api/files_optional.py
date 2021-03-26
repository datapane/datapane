from packaging import version as v
from packaging.specifiers import SpecifierSet

from datapane.common import log

# NOTE - need to update this and keep in sync with JS
BOKEH_V_SPECIFIER = SpecifierSet("~=2.2.0")
PLOTLY_V_SPECIFIER = SpecifierSet(">=4.0.0")
FOLIUM_V_SPECIFIER = SpecifierSet(">=0.12.0")


def _check_version(name: str, _v: v.Version, ss: SpecifierSet):
    if _v not in ss:
        log.warning(
            f"{name} version {_v} is not supported, your plots may not display correctly, please install version {ss}"
        )


# Matplotlib (we don't check version as export to SVG)
try:
    from matplotlib.figure import Axes, Figure
except ImportError:

    class Axes:
        pass

    class Figure:
        pass


# Bokeh
try:
    import bokeh
    from bokeh.layouts import LayoutDOM as BLayout
    from bokeh.plotting.figure import Figure as BFigure

    _check_version("Bokeh", v.Version(bokeh.__version__), BOKEH_V_SPECIFIER)
except ImportError:

    class BLayout:
        pass

    class BFigure:
        pass


# Plotly
try:
    import plotly
    from plotly.graph_objects import Figure as PFigure

    _check_version("Plotly", v.Version(plotly.__version__), PLOTLY_V_SPECIFIER)
except ImportError:

    class PFigure:
        pass


# Folium
try:
    import folium
    from folium import Map

    _check_version("Folium", v.Version(folium.__version__), FOLIUM_V_SPECIFIER)
except ImportError:

    class Map:
        pass
