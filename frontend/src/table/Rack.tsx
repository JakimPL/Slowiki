import type { ReactElement } from "react";

import type { Tile } from "../api/views";
import type { TileBindings } from "./bindings";
import { GraspTile } from "./GraspTile";
import { RACK_LABEL, RETURN_HERE } from "./strings";
import { TileFace } from "./TileFace";

export interface RackProps {
    readonly tiles: readonly Tile[];
    readonly liftedId: number | null;
    readonly bindings: TileBindings | null;
    readonly returnable: boolean;
    readonly onReturn: () => void;
}

export function Rack({ tiles, liftedId, bindings, returnable, onReturn }: RackProps): ReactElement {
    if (bindings === null) {
        return (
            <div className="rack" role="img" aria-label={RACK_LABEL}>
                {tiles.map((tile) => (
                    <TileFace key={tile.identifier} tile={tile} />
                ))}
            </div>
        );
    }
    return (
        <div className="rack" role="group" aria-label={RACK_LABEL} data-region="rack">
            {tiles.map((tile) => (
                <GraspTile
                    key={tile.identifier}
                    tile={tile}
                    spot={{ kind: "rack" }}
                    lifted={tile.identifier === liftedId}
                    bindings={bindings}
                />
            ))}
            {returnable ? (
                <button type="button" className="slot-action" onClick={onReturn}>
                    {RETURN_HERE}
                </button>
            ) : null}
        </div>
    );
}
