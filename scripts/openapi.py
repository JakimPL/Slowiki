import json
from pathlib import Path
from typing import Final

from wordserver.app import create_app

OUTPUT: Final[Path] = Path(__file__).resolve().parents[1] / "frontend" / "openapi.json"
_INDENT: Final = 2


def main(output: Path) -> None:
    document = create_app().openapi()
    body = json.dumps(document, indent=_INDENT, sort_keys=True, ensure_ascii=False) + "\n"
    output.write_text(body, encoding="utf-8")
    print(f"{output}: {len(body)} bytes")


if __name__ == "__main__":
    main(OUTPUT)
