import type { CSSProperties, ReactElement } from "react";

import type { Board as BoardView, Tile } from "../api/views";
import { columnOf, rowOf } from "../play/board";
import { Cell } from "./Cell";
import { BOARD_LABEL, squareCaption } from "./strings";

export interface BoardProps {
    readonly board: BoardView;
    readonly pending: ReadonlyMap<number, Tile>;
    readonly targeting: boolean;
    readonly onLay: ((cell: number) => void) | null;
    readonly onTakeBack: ((cell: number) => void) | null;
}

const CENTER_DIVISOR = 2;

export function Board({ board, pending, targeting, onLay, onTakeBack }: BoardProps): ReactElement {
    const middle = Math.floor(board.size / CENTER_DIVISOR);
    const center = middle * board.size + middle;
    const style: CSSProperties = { "--cells": board.size };
    const interactive = onLay !== null || onTakeBack !== null;
    return (
        <div
            className="board"
            role={interactive ? "group" : "img"}
            aria-label={BOARD_LABEL}
            style={style}
        >
            {board.tiles.map((tile, index) => {
                const shown = pending.get(index) ?? null;
                const tap =
                    shown !== null
                        ? onTakeBack === null
                            ? null
                            : (): void => {
                                  onTakeBack(index);
                              }
                        : onLay === null
                          ? null
                          : (): void => {
                                onLay(index);
                            };
                return (
                    <Cell
                        key={index}
                        tile={tile}
                        bonus={board.bonuses[index] ?? null}
                        star={index === center}
                        pending={shown}
                        target={targeting && tile === null && shown === null && onLay !== null}
                        label={squareCaption(rowOf(board.size, index), columnOf(board.size, index))}
                        onTap={tap}
                    />
                );
            })}
        </div>
    );
}
