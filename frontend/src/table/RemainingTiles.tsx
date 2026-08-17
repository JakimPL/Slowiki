import type { CSSProperties, ReactElement } from "react";

import type { RemainingTally } from "../play/remaining";
import { BLANK_ROW_MARK, REMAINING_LABEL } from "./strings";
import { slugOf } from "./theme";

export interface RemainingTilesProps {
    readonly tally: RemainingTally;
}

export function RemainingTiles({ tally }: RemainingTilesProps): ReactElement {
    return (
        <details className="remaining">
            <summary className="remaining-summary">{REMAINING_LABEL}</summary>
            <ul className="remaining-grid">
                {tally.letters.map((letter) => (
                    <li
                        key={letter.symbol}
                        className="remaining-cell"
                        data-spent={letter.count === 0 ? "true" : undefined}
                        style={faceStyle(letter.category)}
                    >
                        <b>{letter.symbol}</b>
                        <span>{letter.count}</span>
                    </li>
                ))}
                <li className="remaining-cell" data-spent={tally.blanks === 0 ? "true" : undefined}>
                    <b>{BLANK_ROW_MARK}</b>
                    <span>{tally.blanks}</span>
                </li>
            </ul>
        </details>
    );
}

function faceStyle(category: string): CSSProperties {
    return { "--face": `var(--tile-face-${slugOf(category)}, var(--tile-face))` };
}
