from collections.abc import Mapping
from typing import Final

from lexica.artifact.kind import ArtifactKind

ARTIFACT_FORMATS: Final[Mapping[ArtifactKind, int]] = {
    ArtifactKind.WORDS: 1,
    ArtifactKind.RESCUE: 1,
}
