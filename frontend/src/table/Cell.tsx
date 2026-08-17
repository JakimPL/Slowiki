import type { CSSProperties, ReactElement } from "react";

import type { Bonus, Tile } from "../api/views";
import type { TileBindings } from "./bindings";
import { GraspTile } from "./GraspTile";
import { slugOf } from "./theme";
import { TileFace } from "./TileFace";

export interface CellProps {
    readonly cell: number;
    readonly bonus: Bonus | null;
    readonly tile: Tile | null;
    readonly star: boolean;
    readonly pending: Tile | null;
    readonly ghost: Tile | null;
    readonly target: boolean;
    readonly drop: boolean;
    readonly fresh: boolean;
    readonly label: string;
    readonly onLay: ((cell: number) => void) | null;
    readonly bindings: TileBindings | null;
}

const STAR_GLYPH = "✦";

export function Cell({
    cell,
    bonus,
    tile,
    star,
    pending,
    ghost,
    target,
    drop,
    fresh,
    label,
    onLay,
    bindings,
}: CellProps): ReactElement {
    if (tile !== null) {
        return (
            <div className="cell" data-drop={drop ? "true" : undefined} data-fresh={fresh ? "true" : undefined}>
                <TileFace tile={tile} />
            </div>
        );
    }
    if (pending !== null && bindings !== null) {
        return (
            <span className="cell" data-drop={drop ? "true" : undefined}>
                <GraspTile
                    tile={pending}
                    spot={{ kind: "cell", cell }}
                    lifted={false}
                    pending={true}
                    bindings={bindings}
                />
            </span>
        );
    }
    if (pending !== null) {
        return (
            <div className="cell" data-drop={drop ? "true" : undefined}>
                <TileFace tile={pending} pending={true} />
            </div>
        );
    }
    if (ghost !== null) {
        return (
            <div className="cell">
                <TileFace tile={ghost} ghost={true} />
            </div>
        );
    }
    if (target && onLay !== null) {
        return (
            <button
                type="button"
                className="cell cell-button cell-target"
                data-drop={drop ? "true" : undefined}
                aria-label={label}
                onClick={(): void => {
                    onLay(cell);
                }}
            >
                {ground(bonus, star)}
            </button>
        );
    }
    return (
        <div className="cell" data-drop={drop ? "true" : undefined}>
            {ground(bonus, star)}
        </div>
    );
}

function ground(bonus: Bonus | null, star: boolean): ReactElement | null {
    if (bonus !== null) {
        return (
            <i className="cell-premium" style={premiumStyleFor(bonus)}>
                {star ? STAR_GLYPH : glyphFor(bonus)}
            </i>
        );
    }
    return star ? <i className="cell-star">{STAR_GLYPH}</i> : null;
}

function premiumStyleFor(bonus: Bonus): CSSProperties {
    if (bonus.kind === "category_multiplier") {
        const slug = slugOf(bonus.category ?? "");
        return {
            "--fill": `var(--category-${slug}-fill)`,
            "--label": `var(--category-${slug}-label)`,
        };
    }
    const family = bonus.kind === "word_multiplier" ? "word" : "letter";
    const strength = String(bonus.multiplier);
    return {
        "--fill": `var(--premium-${family}-${strength}-fill)`,
        "--label": `var(--premium-${family}-${strength}-label)`,
    };
}

function glyphFor(bonus: Bonus): string {
    const strength = String(bonus.multiplier);
    return bonus.kind === "word_multiplier" ? `${strength}×` : `×${strength}`;
}
