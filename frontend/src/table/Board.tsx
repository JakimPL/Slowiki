import type { CSSProperties, ReactElement } from "react";

import type { Board as BoardView, Tile } from "../api/views";
import { columnOf, rowOf } from "../play/board";
import type { TileBindings } from "./bindings";
import { Cell } from "./Cell";
import { BOARD_LABEL, squareCaption } from "./strings";

export interface BoardProps {
    readonly board: BoardView;
    readonly pending: ReadonlyMap<number, Tile>;
    readonly ghosts: ReadonlyMap<number, Tile>;
    readonly targeting: boolean;
    readonly dropCell: number | null;
    readonly fresh: ReadonlySet<number>;
    readonly freshTint: string | null;
    readonly onLay: ((cell: number) => void) | null;
    readonly bindings: TileBindings | null;
}

const CENTER_DIVISOR = 2;

export function Board({
    board,
    pending,
    ghosts,
    targeting,
    dropCell,
    fresh,
    freshTint,
    onLay,
    bindings,
}: BoardProps): ReactElement {
    const middle = Math.floor(board.size / CENTER_DIVISOR);
    const center = middle * board.size + middle;
    const style: CSSProperties =
        freshTint === null ? { "--cells": board.size } : { "--cells": board.size, "--fresh": freshTint };
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
                        fresh={fresh.has(index)}
                        label={squareCaption(rowOf(board.size, index), columnOf(board.size, index))}
                        onLay={onLay}
                        bindings={bindings}
                    />
                );
            })}
        </div>
    );
}
