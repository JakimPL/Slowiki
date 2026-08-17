import type { ReactElement } from "react";

import type { Tile } from "../api/views";
import type { TileBindings } from "./bindings";
import { GraspTile } from "./GraspTile";
import { rowCountStyle } from "./sizing";
import { RACK_LABEL, RETURN_HERE } from "./strings";
import { TileFace } from "./TileFace";

export interface RackProps {
    readonly tiles: readonly Tile[];
    readonly capacity: number;
    readonly liftedId: number | null;
    readonly locked: ReadonlySet<number>;
    readonly bindings: TileBindings | null;
    readonly returnable: boolean;
    readonly onReturn: () => void;
}

export function Rack({ tiles, capacity, liftedId, locked, bindings, returnable, onReturn }: RackProps): ReactElement {
    if (bindings === null) {
        return (
            <div
                className="rack"
                role="img"
                aria-label={RACK_LABEL}
                style={rowCountStyle(Math.max(capacity, tiles.length))}
            >
                {tiles.map((tile) => (
                    <TileFace key={tile.identifier} tile={tile} />
                ))}
            </div>
        );
    }
    return (
        <div
            className="rack"
            role="group"
            aria-label={RACK_LABEL}
            data-region="rack"
            style={rowCountStyle(Math.max(capacity, tiles.length + (returnable ? 1 : 0)))}
        >
            {tiles.map((tile) =>
                locked.has(tile.identifier) ? (
                    <TileFace key={tile.identifier} tile={tile} ghost={true} />
                ) : (
                    <GraspTile
                        key={tile.identifier}
                        tile={tile}
                        spot={{ kind: "rack" }}
                        lifted={tile.identifier === liftedId}
                        bindings={bindings}
                    />
                ),
            )}
            {returnable ? (
                <button type="button" className="slot-action" onClick={onReturn}>
                    {RETURN_HERE}
                </button>
            ) : null}
        </div>
    );
}
