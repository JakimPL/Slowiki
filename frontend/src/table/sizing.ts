import type { CSSProperties } from "react";

export function rowCountStyle(count: number): CSSProperties {
    return { "--row-count": Math.max(count, 1) };
}
