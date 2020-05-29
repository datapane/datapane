import dataclasses as dc
from typing import Optional

GCR_REGISTRY: str = "eu.gcr.io"


@dc.dataclass
class DockerURI:
    path: dc.InitVar[str]
    image: str = dc.field(init=False)
    namespace: Optional[str] = dc.field(init=False)
    tag: Optional[str] = "latest"
    digest: Optional[str] = None
    domain: str = "docker.io"

    def __post_init__(self, path: str):
        if not (self.tag or self.digest):
            self.tag = "latest"
        # assert self.tag ^ self.digest, "Must have tag or digest"
        # assert self.tag and self.digest, "Image can't have both tag and digest"
        try:
            (self.namespace, self.image) = path.rsplit("/", maxsplit=1)
        except ValueError:
            self.image = path
            self.namespace = None

    # TODO - make a cached property when py3.8+
    @property
    def full_name(self) -> str:
        if self.digest:
            return f"{self.reg_name}@{self.digest}"
        else:
            # NOTE - always set tag as latest if not provided
            t = self.tag or "latest"
            return f"{self.reg_name}:{t}"

    @property
    def reg_name(self) -> str:
        if self.namespace:
            return f"{self.domain}/{self.namespace}/{self.image}"
        else:
            return f"{self.domain}/{self.image}"

    def with_tag(self, tag: str) -> "DockerURI":
        path = f"{self.namespace}/{self.image}" if self.namespace else self.image
        return dc.replace(self, tag=tag, path=path)

    def __str__(self) -> str:
        return self.full_name

    @classmethod
    def mk_internal(cls, image: str, **kwargs) -> "DockerURI":
        return cls(domain=GCR_REGISTRY, path=f"datapane/{image}", **kwargs)
