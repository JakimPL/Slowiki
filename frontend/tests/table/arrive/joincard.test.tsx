import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { JoinCard } from "../../../src/table/arrive/JoinCard";

const NOTHING = (): void => undefined;

function markupOf(code: string): string {
    return renderToStaticMarkup(
        <JoinCard
            code={code}
            arrivals={null}
            busy={false}
            named={true}
            onCode={NOTHING}
            onJoin={NOTHING}
            onInspect={NOTHING}
        />,
    );
}

describe("JoinCard", () => {
    it("reserves two lines under the code field", () => {
        const markup = markupOf("");
        expect(markup).toContain("join-slot");
        expect(markup.match(/join-line/g)?.length).toBe(2);
    });

    it("invites a code before one is entered", () => {
        expect(markupOf("")).toContain("Enter the code from your invitation.");
    });

    it("holds its height whatever the code reads", () => {
        expect(markupOf("KWPZ").match(/join-line/g)?.length).toBe(2);
    });
});
