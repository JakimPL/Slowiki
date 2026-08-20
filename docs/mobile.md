# Mobile packaging

The web app ships to phones in two steps: it is installable as a PWA today, and the same built
bundle wraps into native iOS and Android apps with Capacitor when store presence is wanted. Both
paths reuse everything the project already builds; the game stays an online experience served by
the table server.

## PWA (ready now)

The frontend serves `manifest.webmanifest`, and the asset pipeline generates the icon set it points
at (`assets/icons/`, served under `/artwork/icons/`). After `make build` and a deploy, browsers
offer "Add to Home Screen" and install the table as a standalone app. The layout already handles
the installed context: `100dvh` sizing, safe-area insets, and a `viewport-fit=cover` viewport.

## Capacitor (when store presence is wanted)

Capacitor wraps the built bundle in the platform's own WebView, so the shell stays a few megabytes.
The steps, all inside `frontend/`:

1. `npm install @capacitor/core` and `npm install --save-dev @capacitor/cli`.
2. `npx cap init Slowiki com.example.slowiki --web-dir ../build/frontend`.
3. Point the app at the hosted table server in `capacitor.config.ts`:
   `server: { url: "https://<deployment>" }`. The frontend uses relative URLs throughout, so the
   wrapped app talks to the same API the browser does.
4. `npx cap add android` and `npx cap add ios`, then `npx cap sync` after each `make build`.
5. Export store icons and splash screens from the asset pipeline outputs (`assets/icons/`,
   `assets/brand/splash.svg`).

## Native touches

Platform calls stay behind one small `frontend/src/platform/` module with web fallbacks, so the UI
keeps a single code path:

- haptics on turn start (`@capacitor/haptics`; the web fallback is the existing `navigator.vibrate`
  in `play/alerts.ts`),
- the share sheet for invitations (`@capacitor/share`; the web fallback is the clipboard copy in
  `Invitation`),
- keep-awake during a game (`@capacitor/keep-awake`).

## Constraints the codebase already honors

- Relative API URLs, so one bundle serves the browser, the PWA, and the wrapped app.
- Credentials in the URL hash fragment, so reloads and deep links rejoin a table.
- Safe-area insets and `prefers-reduced-motion` in the stylesheet.
- The stream pauses while the page is hidden (`play/viewing.ts`), which matches mobile lifecycle
  expectations. Switching the turn notice on keeps it connected while hidden, which serves a
  desktop tab well; a backgrounded phone suspends the page either way, so store builds get their
  turn alerts from a push plugin instead.
- One fixed page scale, with the board carrying a scale of its own: the viewport meta pins
  `maximum-scale=1` and the table surface allows panning only, so the browser's pinch and double-tap
  zoom stay out of the way of dragging tiles, while the board region takes every touch itself: a
  two-finger pinch magnifies it up to three times its fitted size, and one finger on a square's own
  ground drags the magnified board into view, bounded so it can never be lost off-screen. In a
  Capacitor shell the page scale comes out the same from the platform WebView — Android sets
  `setBuiltInZoomControls(false)` on the `WebSettings`, iOS keeps the default `WKWebView` behavior
  with this viewport — and the board's own scale rides along inside the page.
