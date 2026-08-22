import type { RefObject } from "react";
import { useLayoutEffect, useRef } from "react";

import type { RowPlace, RowPlaces, Slide } from "../../play/tiles/sliding";
import { slideDuration, slidesBetween } from "../../play/tiles/sliding";

const SLIDE_TOKEN = "--motion-slide";
const SLIDE_EASING = "ease";
const NO_PLACES: RowPlaces = new Map();
const NOTHING_PLAYING: readonly Animation[] = [];

export function useRowSlide(carried: number | null): RefObject<HTMLDivElement | null> {
    const rowRef = useRef<HTMLDivElement | null>(null);
    const placesRef = useRef<RowPlaces>(NO_PLACES);
    const playingRef = useRef<readonly Animation[]>(NOTHING_PLAYING);

    useLayoutEffect(() => {
        const row = rowRef.current;
        if (row === null) {
            return;
        }
        stilled(playingRef.current);
        const places = placesOf(row);
        playingRef.current = carried === null ? slidRow(row, placesRef.current, places) : NOTHING_PLAYING;
        placesRef.current = places;
    });

    return rowRef;
}

function stilled(playing: readonly Animation[]): void {
    for (const animation of playing) {
        animation.cancel();
    }
}

function slidRow(row: HTMLElement, before: RowPlaces, after: RowPlaces): readonly Animation[] {
    const duration = slideDuration(getComputedStyle(row).getPropertyValue(SLIDE_TOKEN));
    if (duration === 0) {
        return NOTHING_PLAYING;
    }
    const playing: Animation[] = [];
    for (const slide of slidesBetween(before, after)) {
        const animation = slid(row, slide, duration);
        if (animation !== null) {
            playing.push(animation);
        }
    }
    return playing;
}

function slid(row: HTMLElement, slide: Slide, duration: number): Animation | null {
    const found = row.querySelector(`[data-tile="${String(slide.id)}"]`);
    if (!(found instanceof HTMLElement)) {
        return null;
    }
    const from = { transform: `translate(${String(slide.dx)}px, ${String(slide.dy)}px)` };
    return found.animate([from, { transform: "translate(0, 0)" }], { duration, easing: SLIDE_EASING });
}

function placesOf(row: HTMLElement): RowPlaces {
    const places = new Map<number, RowPlace>();
    for (const found of row.querySelectorAll("[data-tile]")) {
        placed(places, found);
    }
    return places;
}

function placed(places: Map<number, RowPlace>, found: Element): void {
    if (!(found instanceof HTMLElement)) {
        return;
    }
    const id = Number(found.dataset.tile);
    if (!Number.isInteger(id)) {
        return;
    }
    const rect = found.getBoundingClientRect();
    places.set(id, { left: rect.left, top: rect.top });
}
