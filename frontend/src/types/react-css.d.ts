import "react";

declare module "react" {
    interface CSSProperties {
        [token: `--${string}`]: string | number | undefined;
    }
}
