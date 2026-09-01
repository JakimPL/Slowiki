import type { ReactElement, ReactNode } from "react";

export interface RevealProps {
    readonly open: boolean;
    readonly id: string;
    readonly children: ReactNode;
}

export function Reveal({ open, id, children }: RevealProps): ReactElement {
    return (
        <div className="reveal" data-open={open ? "true" : undefined}>
            <div className="reveal-body" id={id}>
                {children}
            </div>
        </div>
    );
}
