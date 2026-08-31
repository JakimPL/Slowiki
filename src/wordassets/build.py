import shutil
from pathlib import Path
from typing import Final

from wordassets.board import SPECIMEN_WORDS, board_specimen
from wordassets.brand import og_image, splash
from wordassets.drawing.node import document
from wordassets.icons import favicon_ico_bytes, icon_png_bytes, icon_svg_element
from wordassets.manifest import AssetRecord, write_manifest
from wordtable.catalog import ResolvedScheme, list_schemes, resolve_scheme
from wordtable.config import StyleTokens, load_style_tokens, read_config
from wordtable.paths import CONFIG_DIR, RUN_CONFIG_FILE

_ICON_SVG_SIZE: Final = 512.0
_ICON_PNG_SIZES: Final = (192, 512)
_OG_SCHEME: Final = "literaki"


def build_assets(output: Path, docs: Path | None) -> tuple[AssetRecord, ...]:
    tokens = load_style_tokens(CONFIG_DIR, read_config(RUN_CONFIG_FILE).style)
    records = (
        *_specimen_records(output, tokens),
        *_icon_records(output, tokens),
        *_brand_records(output, tokens),
    )
    write_manifest(records, output)
    if docs is not None:
        _copy_specimens(records, output, docs)

    return records


def _specimen_records(
    output: Path,
    tokens: StyleTokens,
) -> tuple[AssetRecord, ...]:
    specimens = output / "specimens"
    specimens.mkdir(parents=True, exist_ok=True)
    records: list[AssetRecord] = []
    for board, resolved in _resolved_by_board().items():
        destination = specimens / f"board-{board}.svg"
        destination.write_text(
            _specimen_document(resolved, tokens),
            encoding="utf-8",
        )
        records.append(
            AssetRecord(
                path=str(destination.relative_to(output)),
                kind="board-specimen",
            )
        )

    return tuple(records)


def _icon_records(output: Path, tokens: StyleTokens) -> tuple[AssetRecord, ...]:
    icons = output / "icons"
    icons.mkdir(parents=True, exist_ok=True)
    theme = tokens.light
    written: list[tuple[str, bytes | str]] = [
        (
            "icon.svg",
            document(
                icon_svg_element(
                    _ICON_SVG_SIZE,
                    theme,
                    maskable=False,
                )
            ),
        ),
        (
            "favicon.svg",
            document(
                icon_svg_element(
                    _ICON_SVG_SIZE,
                    theme,
                    maskable=False,
                )
            ),
        ),
        ("favicon.ico", favicon_ico_bytes(theme)),
    ]
    for size in _ICON_PNG_SIZES:
        written.append(
            (
                f"icon-{size}.png",
                icon_png_bytes(
                    size,
                    theme,
                    maskable=False,
                ),
            )
        )
        written.append(
            (
                f"icon-maskable-{size}.png",
                icon_png_bytes(
                    size,
                    theme,
                    maskable=True,
                ),
            )
        )

    records: list[AssetRecord] = []
    for name, body in written:
        destination = icons / name
        if isinstance(body, str):
            destination.write_text(body, encoding="utf-8")
        else:
            destination.write_bytes(body)

        records.append(
            AssetRecord(
                path=str(destination.relative_to(output)),
                kind="icon",
            )
        )

    return tuple(records)


def _brand_records(
    output: Path,
    tokens: StyleTokens,
) -> tuple[AssetRecord, ...]:
    brand = output / "brand"
    brand.mkdir(parents=True, exist_ok=True)
    tiles = resolve_scheme(CONFIG_DIR, _OG_SCHEME).tiles
    written = (
        ("og-image.svg", document(og_image(tokens.light, tiles))),
        ("splash.svg", document(splash(tokens.light))),
    )
    records: list[AssetRecord] = []
    for name, body in written:
        destination = brand / name
        destination.write_text(body, encoding="utf-8")
        records.append(
            AssetRecord(
                path=str(destination.relative_to(output)),
                kind="brand",
            )
        )

    return tuple(records)


def _resolved_by_board() -> dict[str, ResolvedScheme]:
    by_board: dict[str, ResolvedScheme] = {}
    for name in list_schemes(CONFIG_DIR):
        resolved = resolve_scheme(CONFIG_DIR, name)
        by_board.setdefault(resolved.scheme.board, resolved)
    return by_board


def _specimen_document(resolved: ResolvedScheme, tokens: StyleTokens) -> str:
    word = SPECIMEN_WORDS[resolved.scheme.game]
    return document(board_specimen(resolved.board, resolved.tiles, tokens.light, word))


def _copy_specimens(
    records: tuple[AssetRecord, ...],
    output: Path,
    docs: Path,
) -> None:
    docs.mkdir(parents=True, exist_ok=True)
    for record in records:
        if record.kind == "board-specimen":
            source = output / record.path
            shutil.copyfile(source, docs / source.name)
