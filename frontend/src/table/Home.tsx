import type { ReactElement, SubmitEventHandler } from "react";
import { useEffect, useState } from "react";

import { createTable, joinTable, readOfferings } from "../api/client";
import { reasonOf } from "../api/refusal";
import type { Offering, TableAdmission } from "../api/tables";
import type { Tile } from "../api/views";
import { rememberName, storedName } from "../play/identity";
import { MOVE_INCREMENTS, timeRequestOf, TURN_BUDGETS } from "../play/timing";
import { ModeToggle } from "./ModeToggle";
import {
    budgetCaption,
    CODE_LABEL,
    CREATE_BUTTON,
    CREATE_HEADING,
    INCREMENT_LABEL,
    incrementCaption,
    JOIN_BUTTON,
    JOIN_HEADING,
    NAME_LABEL,
    NAME_PLACEHOLDER,
    offeringCaption,
    OFFERINGS_LOADING,
    PRODUCT_NAME,
    PRODUCT_TAGLINE,
    SCHEME_LABEL,
    SEATS_LABEL,
    SWITCH_TO_CREATE,
    SWITCH_TO_JOIN,
    TIME_LABEL,
    UNTIMED_CAPTION,
} from "./strings";
import { TileFace } from "./TileFace";

export interface HomeProps {
    readonly invitedCode: string | null;
    readonly themeNote: string | null;
    readonly onArrive: (admission: TableAdmission) => void;
}

const SPECIMEN: readonly Tile[] = [
    { identifier: 1, letter: "S", value: 0, category: "yellow", blank: false },
    { identifier: 2, letter: "Ł", value: 0, category: "blue", blank: false },
    { identifier: 3, letter: "O", value: 0, category: "yellow", blank: false },
    { identifier: 4, letter: "W", value: 0, category: "green", blank: false },
    { identifier: 5, letter: "A", value: 0, category: "red", blank: false },
];

export function Home({ invitedCode, themeNote, onArrive }: HomeProps): ReactElement {
    const [offerings, setOfferings] = useState<readonly Offering[] | null>(null);
    const [name, setName] = useState(() => (typeof window === "undefined" ? "" : storedName(window.localStorage)));
    const [code, setCode] = useState(invitedCode ?? "");
    const [schemeName, setSchemeName] = useState<string | null>(null);
    const [seats, setSeats] = useState<number | null>(null);
    const [budget, setBudget] = useState<number | null>(null);
    const [increment, setIncrement] = useState(0);
    const [joining, setJoining] = useState(false);
    const [busy, setBusy] = useState(false);
    const [trouble, setTrouble] = useState<string | null>(null);

    const invited = invitedCode !== null;
    const showJoin = invited || joining;

    useEffect(() => {
        if (invited) {
            return;
        }
        let alive = true;
        readOfferings()
            .then((served) => {
                if (alive) {
                    setOfferings(served);
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
    }, [invited]);

    const chosen = offerings?.find((offering) => offering.name === schemeName) ?? offerings?.[0] ?? null;
    const chosenSeats = boundedSeats(seats, chosen);
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

    const create: SubmitEventHandler<HTMLFormElement> = (submission) => {
        submission.preventDefault();
        if (chosen === null) {
            return;
        }
        const time = timeRequestOf({ totalSeconds: budget, incrementSeconds: increment });
        void settle(() => createTable({ scheme: chosen.name, seats: chosenSeats, name: cleanedName, time }));
    };

    const join: SubmitEventHandler<HTMLFormElement> = (submission) => {
        submission.preventDefault();
        const cleanedCode = code.trim().toUpperCase();
        if (cleanedCode === "") {
            return;
        }
        void settle(() => joinTable(cleanedCode, { name: cleanedName }));
    };

    return (
        <main className="home">
            <div className="home-mode">
                <ModeToggle />
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
            <label className="field home-name">
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
            <div className="home-panels">
                {showJoin ? (
                    <form className="panel" onSubmit={join}>
                        <h2>{JOIN_HEADING}</h2>
                        <label className="field">
                            <span>{CODE_LABEL}</span>
                            <input
                                type="text"
                                className="code-input"
                                value={code}
                                autoCapitalize="characters"
                                onChange={(change): void => {
                                    setCode(change.target.value.toUpperCase());
                                }}
                            />
                        </label>
                        <button type="submit" className="action" disabled={busy || code.trim() === ""}>
                            {JOIN_BUTTON}
                        </button>
                    </form>
                ) : (
                    <form className="panel" onSubmit={create}>
                        <h2>{CREATE_HEADING}</h2>
                        {offerings === null ? (
                            <p className="panel-note">{OFFERINGS_LOADING}</p>
                        ) : (
                            <>
                                <label className="field">
                                    <span>{SCHEME_LABEL}</span>
                                    <select
                                        value={chosen?.name ?? ""}
                                        onChange={(change): void => {
                                            setSchemeName(change.target.value);
                                            setSeats(null);
                                        }}
                                    >
                                        {offerings.map((offering) => (
                                            <option key={offering.name} value={offering.name}>
                                                {offeringCaption(
                                                    offering.name,
                                                    offering.min_players,
                                                    offering.max_players,
                                                )}
                                            </option>
                                        ))}
                                    </select>
                                </label>
                                <label className="field">
                                    <span>{SEATS_LABEL}</span>
                                    <select
                                        value={chosenSeats}
                                        onChange={(change): void => {
                                            setSeats(Number(change.target.value));
                                        }}
                                    >
                                        {chosen === null
                                            ? null
                                            : spanOf(chosen.min_players, chosen.max_players).map((count) => (
                                                  <option key={count} value={count}>
                                                      {count}
                                                  </option>
                                              ))}
                                    </select>
                                </label>
                                <label className="field">
                                    <span>{TIME_LABEL}</span>
                                    <select
                                        value={budget ?? ""}
                                        onChange={(change): void => {
                                            setBudget(change.target.value === "" ? null : Number(change.target.value));
                                        }}
                                    >
                                        <option value="">{UNTIMED_CAPTION}</option>
                                        {TURN_BUDGETS.map((seconds) => (
                                            <option key={seconds} value={seconds}>
                                                {budgetCaption(seconds)}
                                            </option>
                                        ))}
                                    </select>
                                </label>
                                {budget === null ? null : (
                                    <label className="field">
                                        <span>{INCREMENT_LABEL}</span>
                                        <select
                                            value={increment}
                                            onChange={(change): void => {
                                                setIncrement(Number(change.target.value));
                                            }}
                                        >
                                            {MOVE_INCREMENTS.map((seconds) => (
                                                <option key={seconds} value={seconds}>
                                                    {incrementCaption(seconds)}
                                                </option>
                                            ))}
                                        </select>
                                    </label>
                                )}
                            </>
                        )}
                        <button type="submit" className="action" disabled={busy || chosen === null}>
                            {CREATE_BUTTON}
                        </button>
                    </form>
                )}
            </div>
            {invited ? null : (
                <button
                    type="button"
                    className="home-switch"
                    onClick={(): void => {
                        setJoining(!joining);
                    }}
                >
                    {joining ? SWITCH_TO_CREATE : SWITCH_TO_JOIN}
                </button>
            )}
            {trouble === null ? null : (
                <p className="trouble" role="alert">
                    {trouble}
                </p>
            )}
            {themeNote === null ? null : <p className="note">{themeNote}</p>}
        </main>
    );
}

function boundedSeats(seats: number | null, chosen: Offering | null): number {
    if (chosen === null) {
        return 1;
    }
    if (seats === null) {
        return chosen.min_players;
    }
    return Math.min(Math.max(seats, chosen.min_players), chosen.max_players);
}

function spanOf(minimum: number, maximum: number): readonly number[] {
    return Array.from({ length: maximum - minimum + 1 }, (_, offset) => minimum + offset);
}
