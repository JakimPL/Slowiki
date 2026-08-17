import type { Tile } from "../api/views";
import type { DropTarget, TargetMap } from "./targets";
import { resolveTarget } from "./targets";

export type DeskSpot =
    | { readonly kind: "rack" }
    | { readonly kind: "tray" }
    | { readonly kind: "cell"; readonly cell: number };

export interface Grasp {
    readonly spot: DeskSpot;
    readonly tile: Tile;
}

export interface DragPoint {
    readonly x: number;
    readonly y: number;
}

export interface Carry {
    readonly tile: Tile;
    readonly point: DragPoint;
    readonly touch: boolean;
    readonly target: DropTarget | null;
}

export interface GraspSession {
    readonly grasp: Grasp;
    readonly start: DragPoint;
    readonly touch: boolean;
    readonly targets: TargetMap;
    carrying: boolean;
}

export const CARRY_THRESHOLD = 6;

export function isCarry(start: DragPoint, point: DragPoint): boolean {
    const traveled = Math.hypot(point.x - start.x, point.y - start.y);
    return traveled > CARRY_THRESHOLD;
}

export function carriedTo(session: GraspSession, point: DragPoint): Carry {
    return {
        tile: session.grasp.tile,
        point,
        touch: session.touch,
        target: resolveTarget(session.targets, point.x, point.y),
    };
}
