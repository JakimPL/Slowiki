import type { ReactElement } from "react";

import { PASS_BUTTON, RECALL_BUTTON } from "./strings";

export interface ControlsProps {
    readonly caption: string;
    readonly armed: boolean;
    readonly premove: boolean;
    readonly busy: boolean;
    readonly canRecall: boolean;
    readonly canPass: boolean;
    readonly onPlay: () => void;
    readonly onRecall: () => void;
    readonly onPass: () => void;
}

export function Controls({
    caption,
    armed,
    premove,
    busy,
    canRecall,
    canPass,
    onPlay,
    onRecall,
    onPass,
}: ControlsProps): ReactElement {
    return (
        <div className="controls">
            <button
                type="button"
                className="action control-primary"
                data-premove={premove ? "true" : undefined}
                disabled={!armed || busy}
                onClick={onPlay}
            >
                {caption}
            </button>
            <button
                type="button"
                className="control-quiet"
                disabled={!canRecall || busy}
                onClick={onRecall}
            >
                {RECALL_BUTTON}
            </button>
            <button type="button" className="control-quiet" disabled={!canPass || busy} onClick={onPass}>
                {PASS_BUTTON}
            </button>
        </div>
    );
}
