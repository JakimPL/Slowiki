import type { ReactElement } from "react";

import type { LandedRow } from "../../play/board/landing";
import type { DeskSpot } from "../../play/board/spot";
import type { TileBindings } from "../input/bindings";
import { GraspTile } from "./GraspTile";
import { TileFace } from "./TileFace";

export function tileSlots(
    row: LandedRow,
    locked: ReadonlySet<number>,
    spot: DeskSpot,
    bindings: TileBindings,
): readonly ReactElement[] {
    const faces = row.tiles.map((tile) =>
        locked.has(tile.identifier) ? (
            <TileFace key={tile.identifier} tile={tile} ghost={true} />
        ) : (
            <GraspTile key={tile.identifier} tile={tile} spot={spot} bindings={bindings} />
        ),
    );
    if (row.shadowAt === null) {
        return faces;
    }
    const shadow = <span key="landing" className="slot-shadow" aria-hidden="true" />;
    return [...faces.slice(0, row.shadowAt), shadow, ...faces.slice(row.shadowAt)];
}
