from typing import Union

from packaging import version as v
from packaging.specifiers import SpecifierSet

from datapane.common import log


class VersionMismatch(Exception):
    pass


def version_check(provider_v_in: Union[str, v.Version], client_v_in: Union[str, v.Version]):
    """
    Check provider supports client and throws exception if not

    Set the spec so that the client has to be within a micro/patch release of the provider
    NOTE - this isn't semver - breaks when have > v1 release as then treats minor as breaking,
    e.g. 2.2.5 is not compat with 2.1.5
    """
    client_v = v.Version(client_v_in) if isinstance(client_v_in, str) else client_v_in
    provider_v = v.Version(provider_v_in) if isinstance(provider_v_in, str) else provider_v_in

    provider_spec = SpecifierSet(f"~={provider_v.major}.{provider_v.minor}.0")

    log.debug(f"Provider spec {provider_spec}, CLI version {client_v}")
    if client_v not in provider_spec:
        raise VersionMismatch(
            f"Client ({client_v}) and Provider ({provider_spec}) versions not compatible"
        )
