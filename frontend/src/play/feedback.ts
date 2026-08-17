export type FeedbackPolicy = "submit" | "live" | "challenge";

export type WordStatus = "unknown" | "valid" | "invalid" | "standing";

export const INVALID_WORD_CODE = "invalid_word";

const INVALID_PREFIX = "invalid words: ";

export function policyOf(validateOnPlay: boolean): FeedbackPolicy {
    return validateOnPlay ? "submit" : "challenge";
}

export function invalidTextsOf(noticeCode: string | null, notice: string | null): ReadonlySet<string> {
    if (noticeCode !== INVALID_WORD_CODE || !notice?.startsWith(INVALID_PREFIX)) {
        return new Set();
    }
    return new Set(notice.slice(INVALID_PREFIX.length).split(", "));
}

export function wordStatusFor(policy: FeedbackPolicy, text: string, invalidTexts: ReadonlySet<string>): WordStatus {
    if (invalidTexts.has(text)) {
        return "invalid";
    }
    return policy === "challenge" ? "standing" : "unknown";
}
