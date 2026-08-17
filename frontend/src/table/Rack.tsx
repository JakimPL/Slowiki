import type { ReactElement } from "react";

import type { Tile } from "../api/views";
import { RACK_LABEL, tileCaption } from "./strings";
import { TileFace } from "./TileFace";

export interface RackProps {
    readonly tiles: readonly Tile[];
    readonly liftedId: number | null;
    readonly onLift: ((tile: Tile) => void) | null;
}

export function Rack({ tiles, liftedId, onLift }: RackProps): ReactElement {
    if (onLift === null) {
        return (
            <div className="rack" role="img" aria-label={RACK_LABEL}>
                {tiles.map((tile) => (
                    <TileFace key={tile.identifier} tile={tile} />
                ))}
            </div>
        );
    }
    return (
        <div className="rack" role="group" aria-label={RACK_LABEL}>
            {tiles.map((tile) => (
                <button
                    key={tile.identifier}
                    type="button"
                    className="rack-tile"
                    data-lifted={tile.identifier === liftedId ? "true" : undefined}
                    aria-label={tileCaption(tile)}
                    aria-pressed={tile.identifier === liftedId}
                    onClick={(): void => {
                        onLift(tile);
                    }}
                >
                    <TileFace tile={tile} />
                </button>
            ))}
        </div>
    );
}
