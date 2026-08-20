import type { ReactElement, ReactNode } from "react";
import { useRef, useState } from "react";
import type { ReactZoomPanPinchContentRef, ReactZoomPanPinchProps, ReactZoomPanPinchRef } from "react-zoom-pan-pinch";
import { TransformComponent, TransformWrapper } from "react-zoom-pan-pinch";

import { MAX_SCALE, MIN_SCALE, zoomed } from "../../play/board/zoom";
import { BOARD_FIT, BOARD_FIT_LABEL } from "../strings";
import { SQUARE_CONTROL } from "./control";

const GESTURES: ReactZoomPanPinchProps = {
    minScale: MIN_SCALE,
    maxScale: MAX_SCALE,
    limitToBounds: true,
    centerZoomedOut: true,
    panning: {
        excluded: [SQUARE_CONTROL],
        allowLeftClickPan: true,
        allowMiddleClickPan: false,
        allowRightClickPan: false,
        velocityDisabled: true,
    },
    pinch: { allowPanning: true },
    trackPadPanning: { disabled: false },
    doubleClick: { disabled: true },
    wheel: { wheelDisabled: true },
};

const BOARD_VIEW = { "data-region": "board-view" };

export interface BoardStageProps {
    readonly onZoom: () => void;
    readonly children: ReactNode;
}

export function BoardStage({ onZoom, children }: BoardStageProps): ReactElement {
    const controls = useRef<ReactZoomPanPinchContentRef | null>(null);
    const [magnified, setMagnified] = useState(false);
    return (
        <>
            <TransformWrapper
                ref={controls}
                {...GESTURES}
                onZoomStart={onZoom}
                onTransform={(stage: ReactZoomPanPinchRef): void => {
                    setMagnified(zoomed(stage.state.scale));
                }}
            >
                <TransformComponent wrapperClass="board-frame" contentClass="board-stage" wrapperProps={BOARD_VIEW}>
                    {children}
                </TransformComponent>
            </TransformWrapper>
            {magnified ? (
                <button
                    type="button"
                    className="board-fit"
                    aria-label={BOARD_FIT_LABEL}
                    onClick={(): void => {
                        controls.current?.resetTransform();
                    }}
                >
                    {BOARD_FIT}
                </button>
            ) : null}
        </>
    );
}
