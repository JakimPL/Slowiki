export type Connection = "joining" | "live" | "resuming" | "lost";

export function isSettled(connection: Connection): boolean {
    return connection === "live";
}
