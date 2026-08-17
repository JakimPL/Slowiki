import type { CSSProperties, ReactElement } from "react";

import type { Bonus, Tile } from "../api/views";
import { slugOf } from "./theme";
import { TileFace } from "./TileFace";

export interface CellProps {
    readonly bonus: Bonus | null;
    readonly tile: Tile | null;
    readonly star: boolean;
    readonly pending: Tile | null;
    readonly target: boolean;
    readonly label: string;
    readonly onTap: (() => void) | null;
}

const STAR_GLYPH = "✦";

export function Cell({ bonus, tile, star, pending, target, label, onTap }: CellProps): ReactElement {
    if (tile !== null) {
        return (
            <div className="cell">
                <TileFace tile={tile} />
            </div>
        );
    }
    if (pending !== null) {
        return (
            <button type="button" className="cell cell-button" aria-label={label} onClick={onTap ?? undefined}>
                <TileFace tile={pending} pending={true} />
            </button>
        );
    }
    if (target) {
        return (
            <button type="button" className="cell cell-button cell-target" aria-label={label} onClick={onTap ?? undefined}>
                {ground(bonus, star)}
            </button>
        );
    }
    return <div className="cell">{ground(bonus, star)}</div>;
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
