import type { ReactElement } from "react";

import type { Tile } from "../../api/views";
import type { Incoming } from "../../play/board/landing";
import { landedRow } from "../../play/board/landing";
import type { DeskSpot } from "../../play/board/spot";
import type { TileBindings } from "../input/bindings";
import { RACK_LABEL, RETURN_HERE } from "../strings";
import { tileSlots } from "../tiles/slots";
import { TileFace } from "../tiles/TileFace";
import { rowCountStyle } from "./sizing";
import { useRowSlide } from "./useRowSlide";

export interface RackProps {
    readonly tiles: readonly Tile[];
    readonly capacity: number;
    readonly locked: ReadonlySet<number>;
    readonly incoming: Incoming | null;
    readonly bindings: TileBindings | null;
    readonly returnable: boolean;
    readonly onReturn: () => void;
}

const RACK_SPOT: DeskSpot = { kind: "rack" };

export function Rack({ tiles, capacity, locked, incoming, bindings, returnable, onReturn }: RackProps): ReactElement {
    const rowRef = useRowSlide(bindings?.carried ?? null);
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
    const row = landedRow(tiles, incoming);
    const slots = row.tiles.length + (row.shadowAt === null ? 0 : 1) + (returnable ? 1 : 0);
    return (
        <div
            ref={rowRef}
            className="rack"
            role="group"
            aria-label={RACK_LABEL}
            data-region="rack"
            data-drop={incoming === null ? undefined : "true"}
            style={rowCountStyle(Math.max(capacity, slots))}
        >
            {tileSlots(row, locked, RACK_SPOT, bindings)}
            {returnable ? (
                <button type="button" className="slot-action" onClick={onReturn}>
                    {RETURN_HERE}
                </button>
            ) : null}
        </div>
    );
}
