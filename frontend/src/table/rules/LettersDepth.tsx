import type { ReactElement } from "react";

import type { Composing } from "../../play/rules/useComposing";
import { usePresets } from "../../play/rules/usePresets";
import { useSheetFocus } from "../input/useSheetFocus";
import { LETTERS_CLOSE, LETTERS_HEADING, OFFERINGS_LOADING } from "../strings";
import { LettersEditor } from "./LettersEditor";

export interface LettersDepthProps {
    readonly composing: Composing;
    readonly minimum: number;
    readonly maximum: number;
    readonly step: number;
    readonly readOnly: boolean;
    readonly onClose: () => void;
}

export function LettersDepth({
    composing,
    minimum,
    maximum,
    step,
    readOnly,
    onClose,
}: LettersDepthProps): ReactElement {
    const sheet = useSheetFocus<HTMLDivElement>();
    const presets = usePresets();
    const record = composing.record;
    const alphabet = presets?.alphabets.find((held) => held.name === record?.alphabet) ?? null;
    const distribution = presets?.distributions.find((held) => held.name === record?.distribution) ?? null;
    return (
        <div className="sheet-region">
            <button type="button" className="sheet-scrim" aria-label={LETTERS_CLOSE} onClick={onClose} />
            <div
                className="sheet letters-sheet"
                data-depth="2"
                role="dialog"
                aria-label={LETTERS_HEADING}
                tabIndex={-1}
                ref={sheet}
            >
                <h2 className="sheet-heading">{LETTERS_HEADING}</h2>
                {alphabet === null || distribution === null || record === null ? (
                    <p className="menu-note">{OFFERINGS_LOADING}</p>
                ) : (
                    <LettersEditor
                        composing={composing}
                        alphabet={alphabet}
                        distribution={distribution}
                        minimum={minimum}
                        maximum={maximum}
                        step={step}
                        readOnly={readOnly}
                    />
                )}
            </div>
        </div>
    );
}
