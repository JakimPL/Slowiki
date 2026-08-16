import type { CSSProperties, ReactElement } from "react";

import type { Bonus, Tile } from "../api/views";
import { slugOf } from "./theme";
import { TileFace } from "./TileFace";

export interface CellProps {
    readonly bonus: Bonus | null;
    readonly tile: Tile | null;
    readonly star: boolean;
}

const STAR_GLYPH = "✦";

export function Cell({ bonus, tile, star }: CellProps): ReactElement {
    if (tile !== null) {
        return (
            <div className="cell">
                <TileFace tile={tile} />
            </div>
        );
    }
    if (bonus !== null) {
        return (
            <div className="cell">
                <i className="cell-premium" style={premiumStyleFor(bonus)}>
                    {star ? STAR_GLYPH : glyphFor(bonus)}
                </i>
            </div>
        );
    }
    return <div className="cell">{star ? <i className="cell-star">{STAR_GLYPH}</i> : null}</div>;
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
