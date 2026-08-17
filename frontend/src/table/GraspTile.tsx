import type { ReactElement } from "react";

import type { Tile } from "../api/views";
import type { DeskSpot } from "../play/spot";
import type { TileBindings } from "./bindings";
import { tileCaption } from "./strings";
import { TileFace } from "./TileFace";

export interface GraspTileProps {
    readonly tile: Tile;
    readonly spot: DeskSpot;
    readonly pending?: boolean;
    readonly bindings: TileBindings;
}

export function GraspTile({ tile, spot, pending = false, bindings }: GraspTileProps): ReactElement {
    const grasp = { spot, tile };
    const lifted = tile.identifier === bindings.lifted;
    return (
        <button
            type="button"
            className={spot.kind === "cell" ? "cell cell-button" : "rack-tile"}
            data-tile={tile.identifier}
            data-lifted={lifted ? "true" : undefined}
            data-carried={tile.identifier === bindings.carried ? "true" : undefined}
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
        >
            <TileFace tile={tile} pending={pending} />
        </button>
    );
}
