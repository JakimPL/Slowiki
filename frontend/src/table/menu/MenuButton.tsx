import type { ReactElement } from "react";

import { MENU_CAPTION, MENU_LABEL } from "../strings";

export interface MenuButtonProps {
    readonly onOpen: () => void;
}

export function MenuButton({ onOpen }: MenuButtonProps): ReactElement {
    return (
        <button type="button" className="chip chip-menu" aria-label={MENU_LABEL} onClick={onOpen}>
            {MENU_CAPTION}
        </button>
    );
}
