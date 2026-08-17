import type { CSSProperties, ReactElement } from "react";

import type { Tile } from "../api/views";
import { slugOf } from "./theme";

export interface TileFaceProps {
    readonly tile: Tile;
    readonly pending?: boolean;
}

const BLANK_MARK = "◇";

export function TileFace({ tile, pending = false }: TileFaceProps): ReactElement {
    const slug = slugOf(tile.category);
    const style: CSSProperties = {
        "--face": `var(--tile-face-${slug}, var(--tile-face))`,
        "--band": `var(--band-${slug}, transparent)`,
    };
    return (
        <span
            className="tile"
            data-blank={tile.blank ? "true" : undefined}
            data-pending={pending ? "true" : undefined}
            style={style}
        >
            <b className="tile-letter">{tile.letter}</b>
            {tile.value > 0 ? <i className="tile-value">{tile.value}</i> : null}
            {tile.blank ? (
                <i className="tile-mark" aria-hidden="true">
                    {BLANK_MARK}
                </i>
            ) : null}
        </span>
    );
}
