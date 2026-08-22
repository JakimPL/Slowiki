export interface Standing {
    readonly table: string | null;
    readonly token: string | null;
    readonly code: string | null;
    readonly seated: number | null;
}

const TABLE_FIELD = "table";
const TOKEN_FIELD = "token";
const CODE_FIELD = "code";
const SEAT_FIELD = "seat";

export function standingIn(fragment: string): Standing {
    const fields = new URLSearchParams(fragment.replace(/^#/, ""));
    return {
        table: presentIn(fields, TABLE_FIELD),
        token: presentIn(fields, TOKEN_FIELD),
        code: presentIn(fields, CODE_FIELD),
        seated: seatedIn(fields),
    };
}

export function fragmentFor(table: string, token: string, code: string | null, seated: number): string {
    const fields = new URLSearchParams();
    fields.set(TABLE_FIELD, table);
    fields.set(TOKEN_FIELD, token);
    if (code !== null) {
        fields.set(CODE_FIELD, code);
    }
    fields.set(SEAT_FIELD, String(seated));
    return `#${fields.toString()}`;
}

export function withoutFragment(address: string): string {
    const cut = address.indexOf("#");
    return cut === -1 ? address : address.slice(0, cut);
}

export function invitationTo(origin: string, pathname: string, code: string): string {
    const fields = new URLSearchParams();
    fields.set(CODE_FIELD, code);
    return `${origin}${pathname}#${fields.toString()}`;
}

function seatedIn(fields: URLSearchParams): number | null {
    const value = presentIn(fields, SEAT_FIELD);
    if (value === null) {
        return null;
    }
    const parsed = Number(value);
    return Number.isInteger(parsed) && parsed >= 0 ? parsed : null;
}

function presentIn(fields: URLSearchParams, name: string): string | null {
    const value = fields.get(name);
    if (value === null || value === "") {
        return null;
    }
    return value;
}
