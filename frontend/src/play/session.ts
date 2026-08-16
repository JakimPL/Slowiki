export interface Standing {
    readonly table: string | null;
    readonly token: string | null;
    readonly code: string | null;
}

const TABLE_FIELD = "table";
const TOKEN_FIELD = "token";
const CODE_FIELD = "code";

export function standingIn(fragment: string): Standing {
    const fields = new URLSearchParams(fragment.replace(/^#/, ""));
    return {
        table: presentIn(fields, TABLE_FIELD),
        token: presentIn(fields, TOKEN_FIELD),
        code: presentIn(fields, CODE_FIELD),
    };
}

export function fragmentFor(table: string, token: string, code: string | null): string {
    const fields = new URLSearchParams();
    fields.set(TABLE_FIELD, table);
    fields.set(TOKEN_FIELD, token);
    if (code !== null) {
        fields.set(CODE_FIELD, code);
    }
    return `#${fields.toString()}`;
}

export function invitationTo(origin: string, pathname: string, table: string, code: string): string {
    const fields = new URLSearchParams();
    fields.set(TABLE_FIELD, table);
    fields.set(CODE_FIELD, code);
    return `${origin}${pathname}#${fields.toString()}`;
}

function presentIn(fields: URLSearchParams, name: string): string | null {
    const value = fields.get(name);
    if (value === null || value === "") {
        return null;
    }
    return value;
}
