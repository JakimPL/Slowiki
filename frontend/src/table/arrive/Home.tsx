import type { ReactElement } from "react";
import { useEffect, useState } from "react";

import { createTable, joinTable, readOfferings } from "../../api/client";
import { reasonOf } from "../../api/refusal";
import type { OfferingsResponse, RulesConfig, TableAdmission } from "../../api/tables";
import type { Tile } from "../../api/views";
import type { Inspecting } from "../../play/rules/inspecting";
import { useComposing } from "../../play/rules/useComposing";
import { rememberName, storedName } from "../../play/seats/identity";
import { RulesSheet } from "../rules/RulesSheet";
import { LocaleToggle } from "../seats/LocaleToggle";
import { ModeToggle } from "../seats/ModeToggle";
import {
    FORGET_BUTTON,
    NAME_LABEL,
    NAME_PLACEHOLDER,
    PRODUCT_NAME,
    PRODUCT_TAGLINE,
    RETURN_BUTTON,
    SWITCH_TO_CREATE,
    SWITCH_TO_JOIN,
} from "../strings";
import { TileFace } from "../tiles/TileFace";
import { CreateCard } from "./CreateCard";
import { JoinCard } from "./JoinCard";

export interface HomeProps {
    readonly invitedCode: string | null;
    readonly themeNote: string | null;
    readonly onArrive: (admission: TableAdmission) => void;
    readonly onResume: (() => void) | null;
    readonly onForget: () => void;
}

const SPECIMEN: readonly Tile[] = [
    { identifier: 1, letter: "S", value: 0, category: "yellow", blank: false },
    { identifier: 2, letter: "Ł", value: 0, category: "blue", blank: false },
    { identifier: 3, letter: "O", value: 0, category: "yellow", blank: false },
    { identifier: 4, letter: "W", value: 0, category: "yellow", blank: false },
    { identifier: 5, letter: "I", value: 0, category: "yellow", blank: false },
    { identifier: 6, letter: "K", value: 0, category: "green", blank: false },
    { identifier: 7, letter: "I", value: 0, category: "yellow", blank: false },
];

export function Home({ invitedCode, themeNote, onArrive, onResume, onForget }: HomeProps): ReactElement {
    const [arrivals, setArrivals] = useState<OfferingsResponse | null>(null);
    const [name, setName] = useState(() => (typeof window === "undefined" ? "" : storedName(window.localStorage)));
    const [code, setCode] = useState(invitedCode ?? "");
    const [joining, setJoining] = useState(invitedCode !== null);
    const [showingRules, setShowingRules] = useState(false);
    const [inspected, setInspected] = useState<Inspecting | null>(null);
    const [busy, setBusy] = useState(false);
    const [trouble, setTrouble] = useState<string | null>(null);
    const composing = useComposing(arrivals);

    useEffect(() => {
        let alive = true;
        readOfferings()
            .then((served) => {
                if (alive) {
                    setArrivals(served);
                }
            })
            .catch((error: unknown) => {
                if (alive) {
                    setTrouble(reasonOf(error));
                }
            });
        return (): void => {
            alive = false;
        };
    }, []);

    const cleanedName = name.trim() === "" ? null : name.trim();

    const settle = async (action: () => Promise<TableAdmission>): Promise<void> => {
        if (busy) {
            return;
        }
        setBusy(true);
        setTrouble(null);
        try {
            const admission = await action();
            rememberName(cleanedName, window.localStorage);
            onArrive(admission);
        } catch (error: unknown) {
            setTrouble(reasonOf(error));
        } finally {
            setBusy(false);
        }
    };

    const create = (rules: RulesConfig, scheme: string): void => {
        if (cleanedName === null) {
            return;
        }
        void settle(() => createTable({ scheme, name: cleanedName, rules }));
    };

    const join = (): void => {
        if (cleanedName === null) {
            return;
        }
        void settle(() => joinTable(code, { name: cleanedName }));
    };

    return (
        <main className="home">
            <div className="home-mode">
                <ModeToggle />
                <LocaleToggle />
            </div>
            <header className="brand">
                <div className="specimen" aria-hidden="true">
                    {SPECIMEN.map((tile) => (
                        <TileFace key={tile.identifier} tile={tile} />
                    ))}
                </div>
                <h1>{PRODUCT_NAME}</h1>
                <p className="tagline">{PRODUCT_TAGLINE}</p>
            </header>
            <label className="field home-name" data-wanted={cleanedName === null ? "true" : undefined}>
                <span>{NAME_LABEL}</span>
                <input
                    type="text"
                    value={name}
                    placeholder={NAME_PLACEHOLDER}
                    onChange={(change): void => {
                        setName(change.target.value);
                    }}
                />
            </label>
            {onResume === null ? null : (
                <div className="home-return">
                    <button type="button" className="home-switch home-resume" onClick={onResume}>
                        {RETURN_BUTTON}
                    </button>
                    <button type="button" className="home-switch" onClick={onForget}>
                        {FORGET_BUTTON}
                    </button>
                </div>
            )}
            <div className="home-panels">
                {joining ? (
                    <JoinCard
                        code={code}
                        arrivals={arrivals}
                        busy={busy}
                        named={cleanedName !== null}
                        onCode={setCode}
                        onJoin={join}
                        onInspect={setInspected}
                    />
                ) : (
                    <CreateCard
                        composing={composing}
                        busy={busy}
                        named={cleanedName !== null}
                        onCreate={create}
                        onOpenRules={(): void => {
                            setShowingRules(true);
                        }}
                    />
                )}
            </div>
            <button
                type="button"
                className="home-switch"
                onClick={(): void => {
                    setJoining(!joining);
                }}
            >
                {joining ? SWITCH_TO_CREATE : SWITCH_TO_JOIN}
            </button>
            {trouble === null ? null : (
                <p className="trouble" role="alert">
                    {trouble}
                </p>
            )}
            {themeNote === null ? null : <p className="note">{themeNote}</p>}
            {showingRules ? (
                <RulesSheet
                    composing={composing}
                    readOnly={false}
                    onClose={(): void => {
                        setShowingRules(false);
                    }}
                />
            ) : null}
            {inspected === null ? null : (
                <RulesSheet
                    composing={inspected}
                    readOnly={true}
                    onClose={(): void => {
                        setInspected(null);
                    }}
                />
            )}
        </main>
    );
}
