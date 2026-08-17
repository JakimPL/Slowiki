import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Controls } from "../src/table/Controls";

const QUIET = {
    onPrimary: (): void => undefined,
    onRecall: (): void => undefined,
    onShuffle: (): void => undefined,
    onPass: (): void => undefined,
};

describe("Controls", () => {
    it("arms the primary button when a play is ready", () => {
        const markup = renderToStaticMarkup(
            <Controls
                caption="Play · 34"
                armed={true}
                premove={false}
                busy={false}
                canRecall={true}
                canShuffle={true}
                canPass={true}
                {...QUIET}
            />,
        );
        expect(markup).toContain(">Play · 34</button>");
        expect(markup).not.toContain("disabled");
        expect(markup).not.toContain("data-premove");
    });

    it("offers Recall while tiles sit on the board and Shuffle otherwise", () => {
        const drafting = renderToStaticMarkup(
            <Controls
                caption="Play"
                armed={true}
                premove={false}
                busy={false}
                canRecall={true}
                canShuffle={true}
                canPass={true}
                {...QUIET}
            />,
        );
        expect(drafting).toContain(">Recall</button>");
        expect(drafting).not.toContain(">Shuffle</button>");
        const resting = renderToStaticMarkup(
            <Controls
                caption="Play"
                armed={false}
                premove={false}
                busy={false}
                canRecall={false}
                canShuffle={true}
                canPass={true}
                {...QUIET}
            />,
        );
        expect(resting).toContain(">Shuffle</button>");
        expect(resting).not.toContain(">Recall</button>");
    });

    it("shows the premove styling off turn", () => {
        const markup = renderToStaticMarkup(
            <Controls
                caption="Premove · 21"
                armed={true}
                premove={true}
                busy={false}
                canRecall={false}
                canShuffle={true}
                canPass={true}
                {...QUIET}
            />,
        );
        expect(markup).toContain(">Premove · 21</button>");
        expect(markup).toContain('data-premove="true"');
    });

    it("carries an exchange caption for a staged tray", () => {
        const markup = renderToStaticMarkup(
            <Controls
                caption="Exchange 3"
                armed={true}
                premove={false}
                busy={false}
                canRecall={false}
                canShuffle={true}
                canPass={true}
                {...QUIET}
            />,
        );
        expect(markup).toContain(">Exchange 3</button>");
    });

    it("disables everything while a command is in flight", () => {
        const markup = renderToStaticMarkup(
            <Controls
                caption="Play"
                armed={true}
                premove={false}
                busy={true}
                canRecall={true}
                canShuffle={true}
                canPass={true}
                {...QUIET}
            />,
        );
        expect(markup.match(/disabled/g)).toHaveLength(3);
    });
});
