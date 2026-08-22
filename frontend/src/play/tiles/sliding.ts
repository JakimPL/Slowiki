export interface RowPlace {
    readonly left: number;
    readonly top: number;
}

export type RowPlaces = ReadonlyMap<number, RowPlace>;

export interface Slide {
    readonly id: number;
    readonly dx: number;
    readonly dy: number;
}

const STILL_WITHIN = 0.5;
const SECOND_MS = 1000;
const SECONDS = "s";
const MILLISECONDS = "ms";

export function slidesBetween(before: RowPlaces, after: RowPlaces): readonly Slide[] {
    const slides: Slide[] = [];
    for (const [id, place] of after) {
        const slide = slideOf(id, before.get(id), place);
        if (slide !== null) {
            slides.push(slide);
        }
    }
    return slides;
}

export function slideDuration(raw: string): number {
    const value = raw.trim();
    if (value.endsWith(MILLISECONDS)) {
        return positive(value.slice(0, -MILLISECONDS.length));
    }
    if (value.endsWith(SECONDS)) {
        return positive(value.slice(0, -SECONDS.length)) * SECOND_MS;
    }
    return 0;
}

function slideOf(id: number, was: RowPlace | undefined, place: RowPlace): Slide | null {
    if (was === undefined) {
        return null;
    }
    const dx = was.left - place.left;
    const dy = was.top - place.top;
    if (Math.abs(dx) <= STILL_WITHIN && Math.abs(dy) <= STILL_WITHIN) {
        return null;
    }
    return { id, dx, dy };
}

function positive(digits: string): number {
    const parsed = Number(digits);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
}
