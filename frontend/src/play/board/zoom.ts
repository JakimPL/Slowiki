export const MIN_SCALE = 1;
export const MAX_SCALE = 3;

const FITTED_TOLERANCE = 0.01;

export function zoomed(scale: number): boolean {
    return scale > MIN_SCALE + FITTED_TOLERANCE;
}
