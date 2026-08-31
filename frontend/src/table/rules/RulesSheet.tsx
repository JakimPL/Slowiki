import type { ReactElement } from "react";

import type { Composing } from "../../play/rules/useComposing";
import { RULES_CLOSE, RULES_HEADING, RULES_REVERT_ALL } from "../strings";

export interface RulesSheetProps {
    readonly composing: Composing;
    readonly onClose: () => void;
}

export function RulesSheet({ composing, onClose }: RulesSheetProps): ReactElement {
    return (
        <div className="sheet-region">
            <button type="button" className="sheet-scrim" aria-label={RULES_CLOSE} onClick={onClose} />
            <div className="sheet rules-sheet" data-depth="1" role="dialog" aria-label={RULES_HEADING}>
                <h2 className="sheet-heading">{RULES_HEADING}</h2>
                <button
                    type="button"
                    className="action-quiet"
                    disabled={composing.deviations.length === 0}
                    onClick={composing.revertAll}
                >
                    {RULES_REVERT_ALL}
                </button>
            </div>
        </div>
    );
}
