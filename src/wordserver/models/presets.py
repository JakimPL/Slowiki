from wordcore.board.preset import BoardPreset
from wordcore.models.base import BaseFrozen
from wordtable.presets.alphabet import AlphabetPreset
from wordtable.presets.distribution import DistributionPreset


class PresetsResponse(BaseFrozen):
    boards: tuple[BoardPreset, ...]
    alphabets: tuple[AlphabetPreset, ...]
    distributions: tuple[DistributionPreset, ...]
