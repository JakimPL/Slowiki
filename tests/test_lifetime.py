from wordserver.fate import TableFate
from wordserver.lifetime import TableStanding, fate_of
from wordtable.config import TablesConfig

BOUNDS = TablesConfig(life_seconds=100.0, linger_seconds=10.0, sweep_seconds=1.0)


def test_a_table_within_its_life_is_kept() -> None:
    standing = TableStanding(age=99.0, finished_for=None)
    assert fate_of(standing, BOUNDS) is TableFate.KEEP


def test_a_game_standing_past_its_life_is_abandoned() -> None:
    standing = TableStanding(age=100.0, finished_for=None)
    assert fate_of(standing, BOUNDS) is TableFate.ABANDON


def test_a_finished_table_waits_while_its_standing_is_read() -> None:
    standing = TableStanding(age=1000.0, finished_for=9.0)
    assert fate_of(standing, BOUNDS) is TableFate.KEEP


def test_a_finished_table_closes_once_the_linger_is_over() -> None:
    standing = TableStanding(age=1000.0, finished_for=10.0)
    assert fate_of(standing, BOUNDS) is TableFate.CLOSE
