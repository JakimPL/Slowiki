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
