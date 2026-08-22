import type { ReactElement } from "react";
import { useEffect, useState } from "react";

import { readStyle } from "./api/client";
import { useTable } from "./play/live/useTable";
import type { Arrival } from "./play/seats/useStanding";
import { useStanding } from "./play/seats/useStanding";
import { finished } from "./play/story/ending";
import { Home } from "./table/arrive/Home";
import { JOINING_CAPTION, STYLE_FALLBACK_NOTE } from "./table/strings";
import { Table } from "./table/Table";
import { applyTheme } from "./table/theme";
import { Waiting } from "./table/Waiting";

export function App(): ReactElement {
    const [themeNote, setThemeNote] = useState<string | null>(null);
    const { arrival, invitation, arrive, leave, resume, forget } = useStanding();

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
        return (
            <Home
                key={invitation ?? ""}
                invitedCode={invitation}
                themeNote={themeNote}
                onArrive={arrive}
                onResume={resume}
                onForget={forget}
            />
        );
    }
    return <TableScreen arrival={arrival} onLeave={leave} onFinished={forget} />;
}

interface TableScreenProps {
    readonly arrival: Arrival;
    readonly onLeave: () => void;
    readonly onFinished: () => void;
}

function TableScreen({ arrival, onLeave, onFinished }: TableScreenProps): ReactElement {
    const { connection, state, clock, trouble, refresh } = useTable(arrival.seat.table, arrival.seat.token);
    const over = state !== null && finished(state.view.phase);

    useEffect(() => {
        if (over) {
            onFinished();
        }
    }, [over, onFinished]);

    if (state === null) {
        return <Waiting note={trouble ?? JOINING_CAPTION} onLeave={trouble === null ? null : onLeave} />;
    }
    return (
        <Table
            arrival={arrival}
            connection={connection}
            state={state}
            clock={clock}
            trouble={trouble}
            onOutdated={refresh}
            onLeave={onLeave}
        />
    );
}
