import type { ReactElement } from "react";
import { Fragment } from "react";

import type { InflectedForm, LoreReading } from "../../api/lore";
import type { ParadigmGrid, ParadigmList, ParadigmRow } from "../../play/lore/paradigm";
import { paradigmOf } from "../../play/lore/paradigm";
import {
    formCaption,
    odmianaCaption,
    PARADIGM_BACK,
    PARADIGM_BACK_LABEL,
    PARADIGM_GAP,
    PARADIGM_OTHER_FORMS,
    PARADIGM_PLAIN_FORMS,
} from "../strings";

const KEY_SEPARATOR = "|";

export interface WordParadigmProps {
    readonly readings: readonly LoreReading[];
    readonly reading: LoreReading;
    readonly word: string;
    readonly onChoose: (lexeme: string) => void;
    readonly onRetreat: () => void;
}

export function WordParadigm({ readings, reading, word, onChoose, onRetreat }: WordParadigmProps): ReactElement {
    const paradigm = paradigmOf(reading);
    const homonym = readings.length > 1;
    return (
        <div className="paradigm">
            <div className="paradigm-bar">
                <button type="button" className="paradigm-back" aria-label={PARADIGM_BACK_LABEL} onClick={onRetreat}>
                    {PARADIGM_BACK}
                </button>
                {homonym ? <ReadingStrip readings={readings} chosen={reading.lexeme} onChoose={onChoose} /> : null}
            </div>
            <h3 className="paradigm-title">
                <span className="word-part">{reading.part}</span>
                {formCaption(reading.base)}
                {paradigm.heading.length === 0 ? null : (
                    <span className="paradigm-axes">{odmianaCaption(paradigm.heading)}</span>
                )}
            </h3>
            {paradigm.grids.map((grid) => (
                <Grid key={keyOfGrid(grid)} grid={grid} word={word} />
            ))}
            <Lists lists={paradigm.lists} rest={paradigm.rest} word={word} />
        </div>
    );
}

interface ReadingStripProps {
    readonly readings: readonly LoreReading[];
    readonly chosen: string;
    readonly onChoose: (lexeme: string) => void;
}

function ReadingStrip({ readings, chosen, onChoose }: ReadingStripProps): ReactElement {
    return (
        <ul className="paradigm-strip">
            {readings.map((reading) => (
                <li key={reading.lexeme}>
                    <button
                        type="button"
                        className="paradigm-tab"
                        aria-pressed={reading.lexeme === chosen}
                        onClick={(): void => {
                            onChoose(reading.lexeme);
                        }}
                    >
                        <span className="word-part">{reading.part}</span>
                        {formCaption(reading.base)}
                    </button>
                </li>
            ))}
        </ul>
    );
}

interface GridProps {
    readonly grid: ParadigmGrid;
    readonly word: string;
}

function Grid({ grid, word }: GridProps): ReactElement {
    const columns = grid.columns;
    return (
        <div className="paradigm-frame">
            <table className="paradigm-grid">
                {grid.titles.length === 0 ? null : <caption>{odmianaCaption(grid.titles)}</caption>}
                {columns === null ? null : (
                    <thead>
                        <tr>
                            <td />
                            {columns.terms.map((term) => (
                                <th key={term} scope="col">
                                    {term}
                                </th>
                            ))}
                        </tr>
                    </thead>
                )}
                <tbody>
                    {grid.rows.map((row) => (
                        <Row key={row.term} row={row} word={word} />
                    ))}
                </tbody>
            </table>
        </div>
    );
}

interface RowProps {
    readonly row: ParadigmRow;
    readonly word: string;
}

function Row({ row, word }: RowProps): ReactElement {
    return (
        <tr>
            <th scope="row">{row.term}</th>
            {row.cells.map((cell, column) => (
                <td key={keyOf([row.term, String(column)])}>
                    <Cell forms={cell.forms} word={word} />
                </td>
            ))}
        </tr>
    );
}

interface FormsProps {
    readonly forms: readonly InflectedForm[];
    readonly word: string;
}

function Cell({ forms, word }: FormsProps): ReactElement {
    if (forms.length === 0) {
        return <span className="paradigm-gap">{PARADIGM_GAP}</span>;
    }
    return <Forms forms={forms} word={word} />;
}

function Forms({ forms, word }: FormsProps): ReactElement {
    return (
        <>
            {forms.map((form) => (
                <span
                    key={form.text}
                    className="paradigm-form"
                    data-playable={form.playable ? undefined : "false"}
                    data-standing={form.text === word ? "true" : undefined}
                >
                    {formCaption(form.text)}
                </span>
            ))}
        </>
    );
}

interface ListsProps {
    readonly lists: readonly ParadigmList[];
    readonly rest: readonly InflectedForm[];
    readonly word: string;
}

function Lists({ lists, rest, word }: ListsProps): ReactElement | null {
    if (lists.length === 0 && rest.length === 0) {
        return null;
    }
    return (
        <dl className="paradigm-lists">
            {lists.map((list) => (
                <Titled key={keyOf(list.titles)} title={titleOf(list)} forms={list.forms} word={word} />
            ))}
            {rest.length === 0 ? null : <Titled title={PARADIGM_OTHER_FORMS} forms={rest} word={word} />}
        </dl>
    );
}

interface TitledProps {
    readonly title: string;
    readonly forms: readonly InflectedForm[];
    readonly word: string;
}

function Titled({ title, forms, word }: TitledProps): ReactElement {
    return (
        <Fragment>
            <dt>{title}</dt>
            <dd>
                <Forms forms={forms} word={word} />
            </dd>
        </Fragment>
    );
}

function titleOf(list: ParadigmList): string {
    return list.titles.length === 0 ? PARADIGM_PLAIN_FORMS : odmianaCaption(list.titles);
}

function keyOfGrid(grid: ParadigmGrid): string {
    return keyOf([grid.rowDimension, grid.columns?.dimension ?? "", ...grid.titles]);
}

function keyOf(terms: readonly string[]): string {
    return terms.join(KEY_SEPARATOR);
}
