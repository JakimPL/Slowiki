import type { ReactElement } from "react";

import type { CompanyView, PositionView } from "../../api/views";
import { tintFor } from "../../play/seats/tints";
import type { Story } from "../../play/story/story";
import {
    GAME_OVER_CLOSE,
    GAME_OVER_DISMISS,
    GAME_OVER_HEADING,
    GAME_OVER_LEAVE,
    nameFor,
    wonCaption,
} from "../strings";

export interface GameOverProps {
    readonly view: PositionView;
    readonly company: CompanyView;
    readonly story: Story;
    readonly onClose: () => void;
    readonly onLeave: () => void;
}

export function GameOver({ view, company, story, onClose, onLeave }: GameOverProps): ReactElement {
    const ranked = [...view.players].sort(
        (left, right) => (view.scores[String(right)] ?? 0) - (view.scores[String(left)] ?? 0),
    );
    const winners = story.seats.map((seat) => nameFor(company, seat));
    return (
        <section className="game-over">
            <button type="button" className="game-over-scrim" aria-label={GAME_OVER_DISMISS} onClick={onClose} />
            <div className="game-over-card" role="dialog" aria-label={GAME_OVER_HEADING}>
                <h2>{GAME_OVER_HEADING}</h2>
                <p className="game-over-verdict">{wonCaption(winners, story.points ?? 0)}</p>
                <ol className="standing">
                    {ranked.map((seat) => (
                        <li key={seat} className="standing-row" style={{ "--tint": tintFor(seat).hex }}>
                            <span className="standing-name">{nameFor(company, seat)}</span>
                            <span className="standing-score">{view.scores[String(seat)] ?? 0}</span>
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
