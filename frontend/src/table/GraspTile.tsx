import type { ReactElement } from "react";

import type { Tile } from "../api/views";
import type { TileBindings } from "./bindings";
import type { DeskSpot } from "./dragging";
import { tileCaption } from "./strings";
import { TileFace } from "./TileFace";

export interface GraspTileProps {
    readonly tile: Tile;
    readonly spot: DeskSpot;
    readonly lifted: boolean;
    readonly pending?: boolean;
    readonly bindings: TileBindings;
}

export function GraspTile({ tile, spot, lifted, pending = false, bindings }: GraspTileProps): ReactElement {
    const grasp = { spot, tile };
    return (
        <button
            type="button"
            className={spot.kind === "cell" ? "cell cell-button" : "rack-tile"}
            data-tile={tile.identifier}
            data-lifted={lifted ? "true" : undefined}
            aria-label={tileCaption(tile)}
            aria-pressed={lifted}
            onClick={(activation): void => {
                if (activation.detail === 0) {
                    bindings.onTap(grasp);
                }
            }}
            onPointerDown={(event): void => {
                bindings.onDown(grasp, event);
            }}
            onPointerMove={bindings.onMove}
            onPointerUp={bindings.onUp}
            onPointerCancel={bindings.onCancel}
        >
            <TileFace tile={tile} pending={pending} />
        </button>
    );
}
