import type { ReactElement } from "react";
import { useEffect, useState } from "react";

import { readStyle } from "./api/client";
import type { Arrival } from "./play/useStanding";
import { useStanding } from "./play/useStanding";
import { useTable } from "./play/useTable";
import { Home } from "./table/Home";
import { JOINING_CAPTION, STYLE_FALLBACK_NOTE } from "./table/strings";
import { Table } from "./table/Table";
import { applyTheme } from "./table/theme";

export function App(): ReactElement {
    const [themeNote, setThemeNote] = useState<string | null>(null);
    const { arrival, invitation, arrive } = useStanding();

    useEffect(() => {
        let mounted = true;
        readStyle()
            .then((style) => {
                applyTheme(style, document);
            })
            .catch(() => {
                if (mounted) {
                    setThemeNote(STYLE_FALLBACK_NOTE);
                }
            });
        return (): void => {
            mounted = false;
        };
    }, []);

    if (arrival === null) {
        return <Home invitedCode={invitation} themeNote={themeNote} onArrive={arrive} />;
    }
    return <TableScreen arrival={arrival} />;
}

interface TableScreenProps {
    readonly arrival: Arrival;
}

function TableScreen({ arrival }: TableScreenProps): ReactElement {
    const { connection, state, trouble } = useTable(arrival.seat.table, arrival.seat.token);
    if (state === null) {
        return (
            <main className="waiting">
                <p role="status">{trouble ?? JOINING_CAPTION}</p>
            </main>
        );
    }
    return <Table arrival={arrival} connection={connection} state={state} trouble={trouble} />;
}
