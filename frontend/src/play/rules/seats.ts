import type { RulesConfig, SettingAllowance } from "../../api/tables";

const ONE_SEAT: readonly number[] = [1];

export function seatsOffered(rules: RulesConfig | null, allowance: SettingAllowance | null): readonly number[] {
    const rackSize = rules?.rack_size ?? null;
    const minimum = allowance?.minimum ?? null;
    const maximum = allowance?.maximum ?? null;
    if (rackSize === null || minimum === null || maximum === null) {
        return ONE_SEAT;
    }
    return spanOf(minimum, maximum);
}

function spanOf(minimum: number, maximum: number): readonly number[] {
    return Array.from({ length: maximum - minimum + 1 }, (_, offset) => minimum + offset);
}
