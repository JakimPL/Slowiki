import type { CSSProperties, ReactElement } from "react";

import type { Board as BoardView } from "../api/views";
import { Cell } from "./Cell";
import { BOARD_LABEL } from "./strings";

export interface BoardProps {
    readonly board: BoardView;
}

const CENTER_DIVISOR = 2;

export function Board({ board }: BoardProps): ReactElement {
    const middle = Math.floor(board.size / CENTER_DIVISOR);
    const center = middle * board.size + middle;
    const style: CSSProperties = { "--cells": board.size };
    return (
        <div className="board" role="img" aria-label={BOARD_LABEL} style={style}>
            {board.tiles.map((tile, index) => (
                <Cell key={index} tile={tile} bonus={board.bonuses[index] ?? null} star={index === center} />
            ))}
        </div>
    );
}
