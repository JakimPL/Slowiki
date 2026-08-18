import type { PositionView } from "../../api/views";
import type { TableRules } from "../live/rules";

export type ExchangeBlock = "bag-low" | "limit-spent" | null;

export interface ExchangeProspect {
    readonly count: number;
    readonly allowed: boolean;
    readonly block: ExchangeBlock;
    readonly remaining: number | null;
}

export function exchangeProspectOf(
    count: number,
    view: PositionView,
    mySeat: number,
    rules: TableRules,
): ExchangeProspect {
    const used = view.exchange_counts[String(mySeat)] ?? 0;
    const remaining = rules.exchangeLimit === null ? null : Math.max(0, rules.exchangeLimit - used);
    const block = blockOf(view.bag_count, rules, remaining);
    return {
        count,
        allowed: count > 0 && block === null,
        block,
        remaining,
    };
}

function blockOf(bagCount: number, rules: TableRules, remaining: number | null): ExchangeBlock {
    if (bagCount < rules.exchangeMinBag) {
        return "bag-low";
    }
    if (remaining !== null && remaining === 0) {
        return "limit-spent";
    }
    return null;
}
