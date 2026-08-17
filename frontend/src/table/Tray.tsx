import type { ReactElement } from "react";

import type { Tile } from "../api/views";
import type { TileBindings } from "./bindings";
import { GraspTile } from "./GraspTile";
import { PARK_HERE, TRAY_HINT, TRAY_LABEL } from "./strings";
import { TileFace } from "./TileFace";

export interface TrayProps {
    readonly tiles: readonly Tile[];
    readonly liftedId: number | null;
    readonly locked: ReadonlySet<number>;
    readonly bindings: TileBindings;
    readonly parkable: boolean;
    readonly onPark: () => void;
}

export function Tray({ tiles, liftedId, locked, bindings, parkable, onPark }: TrayProps): ReactElement {
    return (
        <div className="tray" role="group" aria-label={TRAY_LABEL} data-region="tray">
            {tiles.map((tile) =>
                locked.has(tile.identifier) ? (
                    <TileFace key={tile.identifier} tile={tile} ghost={true} />
                ) : (
                    <GraspTile
                        key={tile.identifier}
                        tile={tile}
                        spot={{ kind: "tray" }}
                        lifted={tile.identifier === liftedId}
                        bindings={bindings}
                    />
                ),
            )}
            {parkable ? (
                <button type="button" className="slot-action" onClick={onPark}>
                    {PARK_HERE}
                </button>
            ) : null}
            {tiles.length === 0 && !parkable ? <p className="tray-hint">{TRAY_HINT}</p> : null}
        </div>
    );
}
