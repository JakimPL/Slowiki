import type { ReactElement } from "react";

import type { Tile } from "../api/views";
import type { Incoming } from "../play/landing";
import { landedRow } from "../play/landing";
import type { DeskSpot } from "../play/spot";
import type { TileBindings } from "./bindings";
import { tileSlots } from "./slots";
import { PARK_HERE, TRAY_HINT, TRAY_LABEL } from "./strings";

export interface TrayProps {
    readonly tiles: readonly Tile[];
    readonly locked: ReadonlySet<number>;
    readonly incoming: Incoming | null;
    readonly bindings: TileBindings;
    readonly parkable: boolean;
    readonly onPark: () => void;
}

const TRAY_SPOT: DeskSpot = { kind: "tray" };

export function Tray({ tiles, locked, incoming, bindings, parkable, onPark }: TrayProps): ReactElement {
    const row = landedRow(tiles, incoming);
    const bare = row.tiles.length === 0 && row.shadowAt === null && !parkable;
    return (
        <div
            className="tray"
            role="group"
            aria-label={TRAY_LABEL}
            data-region="tray"
            data-drop={incoming === null ? undefined : "true"}
        >
            {tileSlots(row, locked, TRAY_SPOT, bindings)}
            {parkable ? (
                <button type="button" className="slot-action" onClick={onPark}>
                    {PARK_HERE}
                </button>
            ) : null}
            {bare ? <p className="tray-hint">{TRAY_HINT}</p> : null}
        </div>
    );
}
