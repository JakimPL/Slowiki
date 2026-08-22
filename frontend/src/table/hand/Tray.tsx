import type { ReactElement } from "react";

import type { Tile } from "../../api/views";
import type { Incoming } from "../../play/board/landing";
import { landedRow } from "../../play/board/landing";
import type { DeskSpot } from "../../play/board/spot";
import type { TileBindings } from "../input/bindings";
import { PARK_HERE, TRAY_HINT, TRAY_LABEL } from "../strings";
import { tileSlots } from "../tiles/slots";
import { useRowSlide } from "./useRowSlide";

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
    const rowRef = useRowSlide(bindings.carried);
    const row = landedRow(tiles, incoming);
    const bare = row.tiles.length === 0 && row.shadowAt === null && !parkable;
    return (
        <div
            ref={rowRef}
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
