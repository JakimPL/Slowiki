import { useEffect, useState } from "react";

import { readInvitation } from "../../api/client";
import { reasonOf } from "../../api/refusal";
import type { TableDescription } from "../../api/tables";
import type { CodeShape } from "../seats/codes";

export interface Invited {
    readonly reading: boolean;
    readonly description: TableDescription | null;
    readonly refused: string | null;
}

const NOTHING: Invited = { reading: false, description: null, refused: null };

export function useInvitation(code: string, shape: CodeShape | null): Invited {
    const [invited, setInvited] = useState<Invited>(NOTHING);
    const complete = shape !== null && code.length === shape.length;

    useEffect(() => {
        if (!complete) {
            setInvited(NOTHING);
            return;
        }
        let alive = true;
        setInvited({ reading: true, description: null, refused: null });
        readInvitation(code)
            .then((description) => {
                if (alive) {
                    setInvited({ reading: false, description, refused: null });
                }
            })
            .catch((error: unknown) => {
                if (alive) {
                    setInvited({ reading: false, description: null, refused: reasonOf(error) });
                }
            });
        return (): void => {
            alive = false;
        };
    }, [code, complete]);

    return invited;
}
