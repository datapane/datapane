import pytest
from packaging.version import Version

from datapane.common import versioning as v
from datapane.common.utils import should_compress_mime_type_for_upload


def test_version():
    assert "1.1.0" == str(Version("1.1.0"))
    v.is_version_compatible(provider_v_in="0.1.0", consumer_v_in="0.1.8")
    v.is_version_compatible(provider_v_in=Version("1.1.0"), consumer_v_in=Version("1.1.8"))
    # NOTE - below not supported as it's not proper semver
    # v.version_check(provider_version_s="2.1.0", client_version_s="2.0.8")
    with pytest.raises(v.VersionMismatch):
        v.is_version_compatible(provider_v_in="0.2.0", consumer_v_in="0.1.8")
    with pytest.raises(v.VersionMismatch):
        v.is_version_compatible(provider_v_in="2.1.0", consumer_v_in="1.1.0")


@pytest.mark.parametrize(
    "mime_type, value",
    [
        # Some common types:
        # - Should compress:
        ("text/html", True),
        ("text/xml", True),
        ("application/json", True),
        ("application/geo+json", True),
        ("application/rss+xml", True),
        ("image/svg+xml", True),
        # - Should not:
        ("audio/mpeg", False),
        ("image/png", False),
        ("video/mp4", False),
        ("application/zip", False),
        # Our special cases:
        ("application/vnd.vegalite.v5+json", True),
        ("application/vnd.datapane.table+html", True),
        ("application/vnd.pickle+binary", True),
        ("application/vnd.apache.arrow+binary", True),
        ("application/x-tgz", False),
    ],
)
def test_should_compress_mime_type(mime_type, value):
    assert should_compress_mime_type_for_upload(mime_type) == value
