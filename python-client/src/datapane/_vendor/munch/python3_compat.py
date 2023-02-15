from six import u, iteritems, iterkeys # pylint: disable=unused-import
try:
    from collections.abc import Mapping  # pylint: disable=unused-import
except ImportError:
    # Legacy Python
    from collections.abc import Mapping  # pylint: disable=unused-import
