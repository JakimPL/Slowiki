import type { CSSProperties, ReactElement } from "react";

import type { Board as BoardView, Tile } from "../../api/views";
import { centerIndex, columnOf, rowOf } from "../../play/board/board";
import type { FreshFrame, FreshMark } from "../../play/story/fresh";
import type { TileBindings } from "../input/bindings";
import type { HoldBinding } from "../input/useHold";
import { HOLD_MILLISECONDS } from "../input/useHold";
import { BOARD_LABEL, squareCaption } from "../strings";
import { Cell } from "./Cell";

export interface BoardProps {
    readonly board: BoardView;
    readonly pending: ReadonlyMap<number, Tile>;
    readonly ghosts: ReadonlyMap<number, Tile>;
    readonly targeting: boolean;
    readonly dropCell: number | null;
    readonly fresh: ReadonlyMap<number, FreshMark>;
    readonly freshFrame: FreshFrame | null;
    readonly freshTint: string | null;
    readonly freshWaving: boolean;
    readonly onLay: ((cell: number) => void) | null;
    readonly bindings: TileBindings | null;
    readonly hold: HoldBinding | null;
}

export function Board({
    board,
    pending,
    ghosts,
    targeting,
    dropCell,
    fresh,
    freshFrame,
    freshTint,
    freshWaving,
    onLay,
    bindings,
    hold,
}: BoardProps): ReactElement {
    const center = centerIndex(board.size);
    const style: CSSProperties = { "--cells": board.size };
    if (freshTint !== null) {
        style["--fresh"] = freshTint;
    }
    if (hold !== null) {
        style["--hold"] = `${String(HOLD_MILLISECONDS)}ms`;
    }
    const interactive = onLay !== null || bindings !== null;
    return (
        <div
            className="board"
            role={interactive ? "group" : "img"}
            aria-label={BOARD_LABEL}
            style={style}
            data-region="board"
        >
            {board.tiles.map((tile, index) => {
                const shown = pending.get(index) ?? null;
                const shadowed = tile === null && shown === null ? (ghosts.get(index) ?? null) : null;
                return (
                    <Cell
                        key={index}
                        cell={index}
                        tile={tile}
                        bonus={board.bonuses[index] ?? null}
                        star={index === center}
                        pending={shown}
                        ghost={shadowed}
                        target={targeting && tile === null && shown === null && shadowed === null && onLay !== null}
                        drop={dropCell === index}
                        fresh={fresh.get(index) ?? null}
                        label={squareCaption(rowOf(board.size, index), columnOf(board.size, index))}
                        onLay={onLay}
                        bindings={bindings}
                        hold={hold}
                    />
                );
            })}
            {freshFrame === null ? null : <div className="board-fresh" style={frameStyleFor(freshFrame)} />}
            {freshFrame === null || !freshWaving ? null : (
                <div className="board-sweep" style={frameStyleFor(freshFrame)} />
            )}
        </div>
    );
}

function frameStyleFor(frame: FreshFrame): CSSProperties {
    return {
        "--frame-row": frame.row,
        "--frame-column": frame.column,
        "--frame-rows": frame.rows,
        "--frame-columns": frame.columns,
    };
}
