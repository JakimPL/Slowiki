import type { Judged } from "./verdicts";

export type FeedbackPolicy = "submit" | "live" | "challenge";

export type WordStatus = "unknown" | "valid" | "invalid" | "standing";

export const INVALID_WORD_CODE = "invalid_word";

const INVALID_PREFIX = "invalid words: ";

export function policyOf(validateOnPlay: boolean, wordCheck: boolean): FeedbackPolicy {
    if (wordCheck) {
        return "live";
    }
    return validateOnPlay ? "submit" : "challenge";
}

export function invalidTextsOf(noticeCode: string | null, notice: string | null): ReadonlySet<string> {
    if (noticeCode !== INVALID_WORD_CODE || !notice?.startsWith(INVALID_PREFIX)) {
        return new Set();
    }
    return new Set(notice.slice(INVALID_PREFIX.length).split(", "));
}

export function wordStatusFor(
    policy: FeedbackPolicy,
    text: string,
    invalidTexts: ReadonlySet<string>,
    judged: Judged,
): WordStatus {
    if (invalidTexts.has(text)) {
        return "invalid";
    }
    if (policy === "live") {
        return liveStatusOf(judged.get(text));
    }
    return policy === "challenge" ? "standing" : "unknown";
}

function liveStatusOf(allowed: boolean | undefined): WordStatus {
    if (allowed === undefined) {
        return "unknown";
    }
    return allowed ? "valid" : "invalid";
}
