import json
from pathlib import Path
from typing import Final

from wordcore.models.base import BaseFrozen

_INDENT: Final = 2


class AssetRecord(BaseFrozen):
    path: str
    kind: str


def write_manifest(records: tuple[AssetRecord, ...], output: Path) -> Path:
    body = {
        "assets": [record.model_dump() for record in sorted(records, key=lambda item: item.path)]
    }
    destination = output / "manifest.json"
    destination.write_text(
        json.dumps(body, indent=_INDENT, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination
