import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Controls } from "../src/table/Controls";

const QUIET = {
    onPlay: (): void => undefined,
    onRecall: (): void => undefined,
    onPass: (): void => undefined,
};

describe("Controls", () => {
    it("arms the primary button when a play is ready", () => {
        const markup = renderToStaticMarkup(
            <Controls
                caption="Play"
                armed={true}
                premove={false}
                busy={false}
                canRecall={true}
                canPass={true}
                {...QUIET}
            />,
        );
        expect(markup).toContain(">Play</button>");
        expect(markup).not.toContain("disabled");
        expect(markup).not.toContain("data-premove");
    });

    it("shows the premove styling off turn", () => {
        const markup = renderToStaticMarkup(
            <Controls
                caption="Premove"
                armed={true}
                premove={true}
                busy={false}
                canRecall={false}
                canPass={true}
                {...QUIET}
            />,
        );
        expect(markup).toContain(">Premove</button>");
        expect(markup).toContain('data-premove="true"');
    });

    it("disables everything while a command is in flight", () => {
        const markup = renderToStaticMarkup(
            <Controls
                caption="Play"
                armed={true}
                premove={false}
                busy={true}
                canRecall={true}
                canPass={true}
                {...QUIET}
            />,
        );
        expect(markup.match(/disabled/g)).toHaveLength(3);
    });
});
