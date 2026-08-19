import type { ReactElement } from "react";

import { PASS_BUTTON, RECALL_BUTTON, SHUFFLE_BUTTON } from "../strings";

export interface ControlsProps {
    readonly caption: string;
    readonly armed: boolean;
    readonly premove: boolean;
    readonly busy: boolean;
    readonly canRecall: boolean;
    readonly canShuffle: boolean;
    readonly canPass: boolean;
    readonly onPrimary: () => void;
    readonly onRecall: () => void;
    readonly onShuffle: () => void;
    readonly onPass: () => void;
}

export function Controls({
    caption,
    armed,
    premove,
    busy,
    canRecall,
    canShuffle,
    canPass,
    onPrimary,
    onRecall,
    onShuffle,
    onPass,
}: ControlsProps): ReactElement {
    return (
        <div className="controls">
            <button type="button" className="control-quiet" disabled={!canPass || busy} onClick={onPass}>
                {PASS_BUTTON}
            </button>
            <button
                type="button"
                className="action control-primary"
                data-premove={premove ? "true" : undefined}
                disabled={!armed || busy}
                onClick={onPrimary}
            >
                {caption}
            </button>
            <button
                type="button"
                className="control-quiet"
                disabled={busy || (!canRecall && !canShuffle)}
                onClick={canRecall ? onRecall : onShuffle}
            >
                {canRecall ? RECALL_BUTTON : SHUFFLE_BUTTON}
            </button>
        </div>
    );
}
