export function bodyOf<T>(text: string): T {
    return JSON.parse(text) as T;
}

export async function parsed<T>(response: Response): Promise<T> {
    return bodyOf<T>(await response.text());
}
