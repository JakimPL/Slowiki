import type { Letter, TableDescription } from "../../api/tables";
import type { FeedbackPolicy } from "../words/feedback";
import { policyOf } from "../words/feedback";

export interface TableRules {
    readonly rackSize: number | null;
    readonly exchangeLimit: number | null;
    readonly exchangeMinBag: number;
    readonly passAllowed: boolean;
    readonly bingoBonus: number;
    readonly premovesAllowed: boolean;
    readonly feedback: FeedbackPolicy;
    readonly lore: boolean;
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
    lore: false,
    alphabet: null,
};

export function rulesFrom(description: TableDescription | null): TableRules {
    if (description === null) {
        return FALLBACK_RULES;
    }
    const rules = description.rules;
    return {
        rackSize: rules.rack_size,
        exchangeLimit: rules.exchange_limit,
        exchangeMinBag: rules.exchange_min_bag,
        passAllowed: rules.pass_allowed,
        bingoBonus: rules.bingo_bonus,
        premovesAllowed: rules.premoves,
        feedback: policyOf(rules.validate_on_play, description.feedback.word_check),
        lore: description.feedback.lore,
        alphabet: description.alphabet,
    };
}
