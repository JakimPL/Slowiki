import type { Tile } from "../../api/views";
import type { Landing } from "../../play/board/landing";
import type { DeskSpot } from "../../play/board/spot";
import type { TargetMap } from "./targets";
import { landingAt, overBoard } from "./targets";

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
    readonly target: Landing | null;
}

export interface GraspSession {
    readonly grasp: Grasp;
    readonly start: DragPoint;
    readonly touch: boolean;
    targets: TargetMap;
    carrying: boolean;
}

export const CARRY_THRESHOLD = 6;
export const CARRY_LIFT = 44;

const SOLE_POINTER = 1;

export function crowded(pointers: ReadonlySet<number>): boolean {
    return pointers.size > SOLE_POINTER;
}

export function isCarry(start: DragPoint, point: DragPoint): boolean {
    const traveled = Math.hypot(point.x - start.x, point.y - start.y);
    return traveled > CARRY_THRESHOLD;
}

export function aimOf(session: GraspSession, point: DragPoint): DragPoint {
    return session.touch ? { x: point.x, y: point.y - CARRY_LIFT } : point;
}

export function aimedOverBoard(session: GraspSession, point: DragPoint): boolean {
    const aim = aimOf(session, point);
    return overBoard(session.targets, aim.x, aim.y);
}

export function carriedTo(session: GraspSession, point: DragPoint): Carry {
    const aim = aimOf(session, point);
    return {
        tile: session.grasp.tile,
        point,
        touch: session.touch,
        target: landingAt(session.targets, aim.x, aim.y),
    };
}
