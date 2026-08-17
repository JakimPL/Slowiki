import hashlib
import json
from pathlib import Path


def compile_input_digests(
    archive: Path,
    polimorf_path: Path | None,
    overrides_path: Path | None,
    dict_id: str,
    mapping_version: int,
) -> dict[str, str]:
    digests = {
        "archive": _file_digest(archive),
        "polimorf": _file_digest(polimorf_path) if polimorf_path is not None else "absent",
        "overrides": _file_digest(overrides_path) if overrides_path is not None else "absent",
        "dict_id": _text_digest(dict_id),
        "mapping_version": _text_digest(str(mapping_version)),
    }
    return dict(sorted(digests.items()))


def load_manifest(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        return {}
    return {str(key): str(value) for key, value in document.items()}


def write_manifest(path: Path, digests: dict[str, str]) -> None:
    body = json.dumps(digests, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(body, encoding="utf-8")


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text_digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
