from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.models.letters import CanonicalSymbol
from wordtable.allowances.bounds import SettingBounds
from wordtable.allowances.catalog import AllowanceCatalog
from wordtable.allowances.name import SettingName
from wordtable.presets.adjustment import LetterAdjustment
from wordtable.rules import RulesConfig


class SettingOutOfRange(InvalidConfiguration):
    pass


def ensure_within_limits(rules: RulesConfig, catalog: AllowanceCatalog) -> None:
    stated: dict[str, object] = rules.model_dump()
    for setting, allowance in catalog.by_setting().items():
        bounds = allowance.bounds()
        if bounds is None:
            continue

        if setting is SettingName.LETTERS:
            _ensure_every_adjustment_stands_inside(bounds, rules.letters)
        else:
            _ensure_the_setting_stands_inside(setting, bounds, stated[setting.value])


def _ensure_the_setting_stands_inside(
    setting: SettingName,
    bounds: SettingBounds,
    value: object,
) -> None:
    asked = value if isinstance(value, int) else None
    if asked is None:
        _ensure_the_limit_may_be_lifted(setting, bounds)
        return

    if not bounds.minimum <= asked <= bounds.maximum:
        raise SettingOutOfRange(
            f"the setting '{setting}' takes a value from {bounds.minimum} to "
            f"{bounds.maximum}, and this table asks for {asked}"
        )


def _ensure_the_limit_may_be_lifted(setting: SettingName, bounds: SettingBounds) -> None:
    if not bounds.unlimited:
        raise SettingOutOfRange(
            f"the setting '{setting}' takes a value from {bounds.minimum} to {bounds.maximum}"
        )


def _ensure_every_adjustment_stands_inside(
    bounds: SettingBounds,
    letters: dict[CanonicalSymbol, LetterAdjustment],
) -> None:
    for symbol, adjustment in sorted(letters.items()):
        _ensure_the_letter_stands_inside(symbol, bounds, adjustment)


def _ensure_the_letter_stands_inside(
    symbol: CanonicalSymbol,
    bounds: SettingBounds,
    adjustment: LetterAdjustment,
) -> None:
    for asked in (adjustment.value, adjustment.count):
        if asked is not None and not bounds.minimum <= asked <= bounds.maximum:
            raise SettingOutOfRange(
                f"the letter {symbol} takes a value and a count from {bounds.minimum} "
                f"to {bounds.maximum}, and this table asks for {asked}"
            )
