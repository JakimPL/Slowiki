import type { ReactElement } from "react";

import type { CompanyView, PositionView } from "../../api/views";
import { tintFor } from "../../play/seats/tints";
import type { Story } from "../../play/story/story";
import { GAME_OVER_HEADING, nameFor, wonCaption } from "../strings";

export interface GameOverProps {
    readonly view: PositionView;
    readonly company: CompanyView;
    readonly story: Story;
}

export function GameOver({ view, company, story }: GameOverProps): ReactElement {
    const ranked = [...view.players].sort(
        (left, right) => (view.scores[String(right)] ?? 0) - (view.scores[String(left)] ?? 0),
    );
    const winners = story.seats.map((seat) => nameFor(company, seat));
    return (
        <section className="game-over">
            <div className="game-over-card">
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
            </div>
        </section>
    );
}
