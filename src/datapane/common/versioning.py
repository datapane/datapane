from typing import Union

from packaging import version as v
from packaging.specifiers import SpecifierSet

from datapane.common import log


class VersionMismatch(Exception):
    pass


def is_version_compatible(
    provider_v_in: Union[str, v.Version],
    consumer_v_in: Union[str, v.Version],
    raise_exception: bool = True,
) -> bool:
    """
    Check provider supports consumer and throws exception if not

    Set the spec so that the consumer has to be within a micro/patch release of the provider
    NOTE - this isn't semver - breaks when have > v1 release as then treats minor as breaking,
    e.g. 2.2.5 is not compat with 2.1.5
    """
    consumer_v = v.Version(consumer_v_in) if isinstance(consumer_v_in, str) else consumer_v_in
    provider_v = v.Version(provider_v_in) if isinstance(provider_v_in, str) else provider_v_in

    provider_spec = SpecifierSet(f"~={provider_v.major}.{provider_v.minor}.0")

    log.debug(f"Provider spec {provider_spec}, Consumer version {consumer_v}")
    if consumer_v not in provider_spec:
        if raise_exception:
            raise VersionMismatch(
                f"Consumer ({consumer_v}) and Provider ({provider_spec}) API versions not compatible"
            )
        return False
    return True
