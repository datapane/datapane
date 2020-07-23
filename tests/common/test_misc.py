import pytest
from packaging.version import Version

from datapane.common import config as c
from datapane.common import versioning as v


def test_encode_decode():
    """Test we can encode/decode a config element"""
    u_config = c.RunnerConfig(script_id="ZBAmDk1", config=dict(a=3))

    # test raw
    e = c.encode(u_config, compressed=False)
    d = c.decode(e, compressed=False)
    assert d == u_config

    # test compressed
    e_c = c.encode(u_config, compressed=True)
    d_c = c.decode(e_c, compressed=True)
    assert d_c == u_config


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
