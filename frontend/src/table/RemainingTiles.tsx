import type { ReactElement } from "react";

import type { RemainingTally } from "../play/remaining";
import { BLANK_ROW_MARK, REMAINING_LABEL } from "./strings";

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
