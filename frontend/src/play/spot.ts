export type DeskSpot =
    { readonly kind: "rack" } | { readonly kind: "tray" } | { readonly kind: "cell"; readonly cell: number };
