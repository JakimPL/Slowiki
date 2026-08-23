from typing import NamedTuple

from lexica.lore.override import OverrideTable
from lexica.lore.rescue import RescueTable
from lexica.sources.sgjp import MorfeuszEngine


class LoreSources(NamedTuple):
    engine: MorfeuszEngine
    rescue: RescueTable
    overrides: OverrideTable
