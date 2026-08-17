import type { Letter, TableDescription } from "../api/tables";
import type { FeedbackPolicy } from "./feedback";
import { policyOf } from "./feedback";

export interface TableRules {
    readonly rackSize: number | null;
    readonly exchangeLimit: number | null;
    readonly exchangeMinBag: number;
    readonly passAllowed: boolean;
    readonly bingoBonus: number;
    readonly premovesAllowed: boolean;
    readonly feedback: FeedbackPolicy;
    readonly alphabet: readonly Letter[] | null;
}

export const FALLBACK_RULES: TableRules = {
    rackSize: null,
    exchangeLimit: null,
    exchangeMinBag: 0,
    passAllowed: true,
    bingoBonus: 0,
    premovesAllowed: false,
    feedback: "submit",
    alphabet: null,
};

export function rulesFrom(description: TableDescription | null): TableRules {
    if (description === null) {
        return FALLBACK_RULES;
    }
    const parameters = description.parameters;
    return {
        rackSize: parameters.rack_size,
        exchangeLimit: parameters.exchange_limit,
        exchangeMinBag: parameters.exchange_min_bag,
        passAllowed: parameters.pass_allowed,
        bingoBonus: parameters.bingo_bonus,
        premovesAllowed: parameters.premoves_allowed,
        feedback: policyOf(parameters.validate_on_play),
        alphabet: description.alphabet,
    };
}
