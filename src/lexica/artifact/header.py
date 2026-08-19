from lexica.artifact.kind import ArtifactKind
from wordcore.models.base import BaseFrozen


class ArtifactHeader(BaseFrozen):
    kind: ArtifactKind
    format: int
    entries: int
