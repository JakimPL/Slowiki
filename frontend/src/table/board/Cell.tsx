import type { CSSProperties, ReactElement } from "react";

import type { Bonus, Tile } from "../../api/views";
import type { FreshMark } from "../../play/story/fresh";
import type { TileBindings } from "../input/bindings";
import type { HoldBinding } from "../input/useHold";
import { slugOf } from "../theme";
import { GraspTile } from "../tiles/GraspTile";
import { TileFace } from "../tiles/TileFace";

export interface CellProps {
    readonly cell: number;
    readonly bonus: Bonus | null;
    readonly tile: Tile | null;
    readonly star: boolean;
    readonly pending: Tile | null;
    readonly ghost: Tile | null;
    readonly target: boolean;
    readonly drop: boolean;
    readonly fresh: FreshMark | null;
    readonly label: string;
    readonly onLay: ((cell: number) => void) | null;
    readonly bindings: TileBindings | null;
    readonly hold: HoldBinding | null;
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
    hold,
}: CellProps): ReactElement {
    if (tile !== null) {
        return (
            <div
                className="cell"
                style={fresh === null ? undefined : waveStyleFor(fresh)}
                data-drop={drop ? "true" : undefined}
                data-fresh={fresh === null ? undefined : "true"}
                data-waving={fresh?.waving === true ? "true" : undefined}
                data-holding={hold?.held === cell ? "true" : undefined}
                onPointerDown={
                    hold === null
                        ? undefined
                        : (): void => {
                              hold.press(cell);
                          }
                }
                onPointerUp={hold?.release}
                onPointerCancel={hold?.release}
                onPointerLeave={hold?.release}
                onTouchEnd={hold?.consumed}
            >
                <TileFace tile={tile} />
            </div>
        );
    }
    if (pending !== null && bindings !== null) {
        return (
            <span className="cell" data-drop={drop ? "true" : undefined}>
                <GraspTile tile={pending} spot={{ kind: "cell", cell }} pending={true} bindings={bindings} />
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
    if (star) {
        return (
            <>
                {premiumFill(bonus)}
                <i className="cell-star">{STAR_GLYPH}</i>
            </>
        );
    }
    if (bonus === null) {
        return null;
    }
    return (
        <i className="cell-premium" style={premiumStyleFor(bonus)}>
            {glyphFor(bonus)}
        </i>
    );
}

function waveStyleFor(fresh: FreshMark): CSSProperties {
    return { "--ordinal": fresh.ordinal };
}

function premiumFill(bonus: Bonus | null): ReactElement | null {
    return bonus === null ? null : <i className="cell-premium" style={premiumStyleFor(bonus)} />;
}

function premiumStyleFor(bonus: Bonus): CSSProperties {
    if (bonus.kind === "category_multiplier") {
        const slug = slugOf(bonus.category ?? "");
        return {
            "--fill": `var(--category-${slug}-fill)`,
            "--glyph": `var(--category-${slug}-glyph)`,
        };
    }
    const family = bonus.kind === "word_multiplier" ? "word" : "letter";
    const strength = String(bonus.multiplier);
    return {
        "--fill": `var(--premium-${family}-${strength}-fill)`,
        "--glyph": `var(--premium-${family}-${strength}-glyph)`,
    };
}

function glyphFor(bonus: Bonus): string {
    const strength = String(bonus.multiplier);
    return bonus.kind === "word_multiplier" ? `${strength}×` : `×${strength}`;
}
