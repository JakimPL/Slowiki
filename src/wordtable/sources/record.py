from pathlib import Path

from wordcore.models.base import BaseFrozen


class ReleaseRecord(BaseFrozen):
    stem: str
    url: str
    sha256: str


def read_release_record(path: Path) -> ReleaseRecord | None:
    if not path.is_file():
        return None

    return ReleaseRecord.model_validate_json(path.read_text(encoding="utf-8"))


def write_release_record(path: Path, record: ReleaseRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record.model_dump_json(indent=2) + "\n", encoding="utf-8")
