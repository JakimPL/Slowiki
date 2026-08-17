import type { GeometryVerdict } from "./geometry";

export type Guidance =
    | "place"
    | "opening-short"
    | "off-center"
    | "detached"
    | "scattered"
    | "gapped"
    | null;

export function guidanceFor(verdict: GeometryVerdict, lifted: boolean): Guidance {
    switch (verdict) {
        case "empty":
            return lifted ? "place" : null;
        case "opening-short":
            return "opening-short";
        case "off-center":
            return "off-center";
        case "detached":
            return "detached";
        case "scattered":
            return "scattered";
        case "gapped":
            return "gapped";
        case "playable":
            return null;
    }
}
