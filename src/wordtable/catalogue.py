from pathlib import Path

from lexica.names import DictionaryName
from wordcore.board.preset import BoardPreset
from wordcore.models.base import BaseFrozen
from wordcore.tiles.tile import TilePreset
from wordgames.names import GameName
from wordtable.config import (
    SchemeConfig,
    load_board_preset,
    load_scheme,
    load_tile_preset,
)
from wordtable.paths import CONFIGURATION_SCHEMES_PATH


class Offering(BaseFrozen):
    name: str
    game: GameName
    dictionary: DictionaryName
    min_players: int
    max_players: int


class ResolvedScheme(BaseFrozen):
    scheme: SchemeConfig
    board: BoardPreset
    tiles: TilePreset


def list_schemes(directory: Path) -> dict[str, SchemeConfig]:
    schemes_dir = directory / CONFIGURATION_SCHEMES_PATH
    return {
        path.stem: load_scheme(
            directory,
            path.stem,
        )
        for path in sorted(schemes_dir.glob("*.yaml"))
    }


def offerings(directory: Path) -> tuple[Offering, ...]:
    return tuple(
        Offering(
            name=name,
            game=scheme.game,
            dictionary=scheme.dictionary,
            min_players=scheme.min_players,
            max_players=scheme.max_players,
        )
        for name, scheme in list_schemes(directory).items()
    )


def resolve_scheme(directory: Path, name: str) -> ResolvedScheme:
    scheme = load_scheme(directory, name)
    return ResolvedScheme(
        scheme=scheme,
        board=load_board_preset(directory, scheme.board),
        tiles=load_tile_preset(directory, scheme.tiles),
    )
