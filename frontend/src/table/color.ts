const HEX_PREFIX = "#";
const HEX_RADIX = 16;
const CHANNEL_LENGTH = 2;
const CHANNEL_COUNT = 3;

export function mixHex(base: string, overlay: string, share: number): string {
    const blended = Array.from({ length: CHANNEL_COUNT }, (_, channel) => {
        const from = channelOf(base, channel);
        const to = channelOf(overlay, channel);
        return Math.round(from + (to - from) * share);
    });
    return HEX_PREFIX + blended.map((value) => value.toString(HEX_RADIX).padStart(CHANNEL_LENGTH, "0")).join("");
}

function channelOf(color: string, channel: number): number {
    const start = HEX_PREFIX.length + channel * CHANNEL_LENGTH;
    return Number.parseInt(color.slice(start, start + CHANNEL_LENGTH), HEX_RADIX);
}
