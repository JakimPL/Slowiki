import type { ReactElement } from "react";

import type { Tile } from "../api/views";
import { RACK_LABEL } from "./strings";
import { TileFace } from "./TileFace";

export interface RackProps {
    readonly tiles: readonly Tile[];
}

export function Rack({ tiles }: RackProps): ReactElement {
    return (
        <div className="rack" role="img" aria-label={RACK_LABEL}>
            {tiles.map((tile) => (
                <TileFace key={tile.identifier} tile={tile} />
            ))}
        </div>
    );
}
