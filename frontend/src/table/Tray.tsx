import type { ReactElement } from "react";

import type { Tile } from "../api/views";
import type { TileBindings } from "./bindings";
import { GraspTile } from "./GraspTile";
import { PARK_HERE, TRAY_HINT, TRAY_LABEL } from "./strings";

export interface TrayProps {
    readonly tiles: readonly Tile[];
    readonly liftedId: number | null;
    readonly bindings: TileBindings;
    readonly parkable: boolean;
    readonly onPark: () => void;
}

export function Tray({ tiles, liftedId, bindings, parkable, onPark }: TrayProps): ReactElement {
    return (
        <div className="tray" role="group" aria-label={TRAY_LABEL} data-region="tray">
            {tiles.map((tile) => (
                <GraspTile
                    key={tile.identifier}
                    tile={tile}
                    spot={{ kind: "tray" }}
                    lifted={tile.identifier === liftedId}
                    bindings={bindings}
                />
            ))}
            {parkable ? (
                <button type="button" className="slot-action" onClick={onPark}>
                    {PARK_HERE}
                </button>
            ) : null}
            {tiles.length === 0 && !parkable ? <p className="tray-hint">{TRAY_HINT}</p> : null}
        </div>
    );
}
