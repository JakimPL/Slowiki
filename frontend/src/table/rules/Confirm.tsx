import type { ReactElement } from "react";

import { CONFIRM_HEADING, CONFIRM_KEEP } from "../strings";

export interface Confirmation {
    readonly sentence: string;
    readonly proceed: string;
    readonly onProceed: () => void;
}

export interface ConfirmProps {
    readonly asked: Confirmation;
    readonly onKeep: () => void;
}

export function Confirm({ asked, onKeep }: ConfirmProps): ReactElement {
    return (
        <div className="confirm">
            <button type="button" className="confirm-scrim" aria-label={CONFIRM_KEEP} onClick={onKeep} />
            <div className="confirm-card" role="alertdialog" aria-label={CONFIRM_HEADING}>
                <h2>{CONFIRM_HEADING}</h2>
                <p className="confirm-sentence">{asked.sentence}</p>
                <div className="confirm-foot">
                    <button type="button" className="action action-quiet" onClick={onKeep}>
                        {CONFIRM_KEEP}
                    </button>
                    <button
                        type="button"
                        className="action"
                        onClick={(): void => {
                            asked.onProceed();
                            onKeep();
                        }}
                    >
                        {asked.proceed}
                    </button>
                </div>
            </div>
        </div>
    );
}
