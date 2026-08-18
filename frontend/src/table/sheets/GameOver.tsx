import type { ReactElement } from "react";

import type { CompanyView, PositionView } from "../../api/views";
import { tintFor } from "../../play/seats/tints";
import { rankingOf } from "../../play/story/ranking";
import type { Story } from "../../play/story/story";
import {
    captionFor,
    GAME_OVER_CLOSE,
    GAME_OVER_DISMISS,
    GAME_OVER_HEADING,
    GAME_OVER_LEAVE,
    GAME_OVER_VICTORY,
    nameFor,
    YOU_MARKER,
} from "../strings";

export interface GameOverProps {
    readonly view: PositionView;
    readonly company: CompanyView;
    readonly story: Story;
    readonly mySeat: number | null;
    readonly onClose: () => void;
    readonly onLeave: () => void;
}

export function GameOver({ view, company, story, mySeat, onClose, onLeave }: GameOverProps): ReactElement {
    const crowned = story.mine && story.seats.length === 1;
    return (
        <section className="game-over">
            <button type="button" className="game-over-scrim" aria-label={GAME_OVER_DISMISS} onClick={onClose} />
            <div
                className="game-over-card"
                role="dialog"
                aria-label={GAME_OVER_HEADING}
                data-mine={story.mine ? "true" : undefined}
            >
                <h2>{story.mine ? GAME_OVER_VICTORY : GAME_OVER_HEADING}</h2>
                {crowned ? null : <p className="game-over-verdict">{captionFor(story, company)}</p>}
                <ol className="standing">
                    {rankingOf(view).map((ranked) => (
                        <li
                            key={ranked.seat}
                            className="standing-row"
                            style={{ "--tint": tintFor(ranked.seat).hex }}
                            data-podium={ranked.podium === null ? undefined : String(ranked.podium)}
                            data-mine={ranked.seat === mySeat ? "true" : undefined}
                        >
                            <span className="standing-place">{ranked.place}</span>
                            <span className="standing-name">{nameFor(company, ranked.seat)}</span>
                            {ranked.seat === mySeat ? <em className="standing-you">{YOU_MARKER}</em> : null}
                            <span className="standing-score">{ranked.points}</span>
                        </li>
                    ))}
                </ol>
                <div className="game-over-actions">
                    <button type="button" className="action" onClick={onClose}>
                        {GAME_OVER_CLOSE}
                    </button>
                    <button type="button" className="action action-quiet" onClick={onLeave}>
                        {GAME_OVER_LEAVE}
                    </button>
                </div>
            </div>
        </section>
    );
}
